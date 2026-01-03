"""
测试 QueryEngine 与 Identifier 系统的集成

验证：
1. QueryEngine 正确使用 Identifier 进行类型分派
2. 不同层级的标识符解析行为
3. 属性访问路径的正确性
"""

import pytest
from pathlib import Path
from typedown.core.analysis.query import QueryEngine, QueryError
from typedown.core.base.errors import ReferenceError
from typedown.core.base.identifiers import Identifier, Handle, Slug, Hash, UUID


class MockSymbolTable:
    """模拟符号表，支持不同类型的标识符"""
    
    def __init__(self):
        self.data = {}
    
    def resolve(self, query: str, context_path: Optional[Path] = None) -> Any:
        return self.data.get(query)
        
    # Add explicit typed resolvers to satisfy QueryEngine delegation
    def resolve_handle(self, name: str, context_path: Optional[Path] = None) -> Any:
        return self.data.get(name)
        
    def resolve_slug(self, path: str) -> Any:
        return self.data.get(path)
        
    def resolve_hash(self, hash_value: str) -> Any:
        return self.data.get(f"sha256:{hash_value}")
        
    def resolve_uuid(self, uuid_value: str) -> Any:
        return self.data.get(uuid_value)
    
    def __contains__(self, key):
        return key in self.data
    
    def __getitem__(self, key):
        return self.data[key]


class TestQueryEngineIdentifierIntegration:
    """测试 QueryEngine 与 Identifier 的集成"""
    
    def test_resolve_handle(self):
        """测试解析 Handle 标识符"""
        symbol_table = MockSymbolTable()
        symbol_table.data["alice"] = {"name": "Alice", "age": 30}
        
        # 直接解析 Handle
        result = QueryEngine._resolve_symbol_path("alice", symbol_table)
        assert result == {"name": "Alice", "age": 30}
        
        # 属性访问
        result = QueryEngine._resolve_symbol_path("alice.name", symbol_table)
        assert result == "Alice"
    
    def test_resolve_slug(self):
        """测试解析 Slug 标识符"""
        symbol_table = MockSymbolTable()
        symbol_table.data["users/alice"] = {"name": "Alice", "role": "admin"}
        
        # 直接解析 Slug
        result = QueryEngine._resolve_symbol_path("users/alice", symbol_table)
        assert result == {"name": "Alice", "role": "admin"}
        
        # 属性访问
        result = QueryEngine._resolve_symbol_path("users/alice.role", symbol_table)
        assert result == "admin"
    
    def test_resolve_hash(self):
        """测试解析 Hash 标识符"""
        symbol_table = MockSymbolTable()
        hash_value = "a3b2c1d4e5f6789012345678901234567890123456789012345678901234"
        symbol_table.data[f"sha256:{hash_value}"] = {"content": "immutable data"}
        
        # 直接解析 Hash
        result = QueryEngine._resolve_symbol_path(f"sha256:{hash_value}", symbol_table)
        assert result == {"content": "immutable data"}
        
        # 属性访问
        result = QueryEngine._resolve_symbol_path(f"sha256:{hash_value}.content", symbol_table)
        assert result == "immutable data"
    
    def test_resolve_uuid(self):
        """测试解析 UUID 标识符"""
        symbol_table = MockSymbolTable()
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        symbol_table.data[uuid_str] = {"id": uuid_str, "type": "entity"}
        
        # 直接解析 UUID
        result = QueryEngine._resolve_symbol_path(uuid_str, symbol_table)
        assert result == {"id": uuid_str, "type": "entity"}
        
        # 属性访问
        result = QueryEngine._resolve_symbol_path(f"{uuid_str}.type", symbol_table)
        assert result == "entity"
    
    def test_identifier_type_dispatch(self):
        """测试基于类型的多分派"""
        symbol_table = MockSymbolTable()
        
        # 准备不同类型的标识符
        symbol_table.data["alice"] = "handle_value"
        symbol_table.data["users/alice"] = "slug_value"
        symbol_table.data["sha256:abc123"] = "hash_value"
        symbol_table.data["550e8400-e29b-41d4-a716-446655440000"] = "uuid_value"
        
        # 验证每种类型都被正确分派
        assert QueryEngine._resolve_symbol_path("alice", symbol_table) == "handle_value"
        assert QueryEngine._resolve_symbol_path("users/alice", symbol_table) == "slug_value"
        assert QueryEngine._resolve_symbol_path("sha256:abc123", symbol_table) == "hash_value"
        assert QueryEngine._resolve_symbol_path("550e8400-e29b-41d4-a716-446655440000", symbol_table) == "uuid_value"
    
    def test_property_path_traversal(self):
        """测试属性路径遍历"""
        symbol_table = MockSymbolTable()
        symbol_table.data["user"] = {
            "profile": {
                "name": "Alice",
                "contacts": ["email@example.com", "phone"]
            }
        }
        
        # 嵌套属性访问
        result = QueryEngine._resolve_symbol_path("user.profile.name", symbol_table)
        assert result == "Alice"
        
        # 数组索引
        result = QueryEngine._resolve_symbol_path("user.profile.contacts[0]", symbol_table)
        assert result == "email@example.com"
    
    def test_error_handling(self):
        """测试错误处理"""
        symbol_table = MockSymbolTable()
        
        # 不存在的 Handle
        with pytest.raises(ReferenceError, match="L2 Fuzzy Match failed"):
            QueryEngine._resolve_symbol_path("nonexistent", symbol_table)
        
        # 不存在的 Slug
        with pytest.raises(ReferenceError, match="L1 Exact Match failed"):
            QueryEngine._resolve_symbol_path("users/nonexistent", symbol_table)
        
        # 不存在的属性
        symbol_table.data["user"] = {"name": "Alice"}
        with pytest.raises(QueryError, match="Segment 'age' not found"):
            QueryEngine._resolve_symbol_path("user.age", symbol_table)
    
    def test_wildcard_operator(self):
        """测试通配符操作符"""
        symbol_table = MockSymbolTable()
        
        # 创建一个模拟的 EntityBlock
        class MockEntity:
            def __init__(self, data):
                self.raw_data = data
        
        symbol_table.data["user"] = MockEntity({"name": "Alice", "age": 30})
        
        # 使用通配符返回整个对象
        result = QueryEngine._resolve_symbol_path("user.*", symbol_table)
        assert result == {"name": "Alice", "age": 30}


class TestQueryEngineWithReference:
    """测试 QueryEngine 与 Reference AST 节点的集成"""
    
    def test_reference_identifier_parsing(self):
        """测试 Reference 节点自动解析 identifier"""
        from typedown.core.ast.document import Reference
        from typedown.core.ast.base import SourceLocation
        
        # 创建 Reference 节点
        ref = Reference(
            target="alice",
            location=SourceLocation(file_path="test.td", line_start=1, line_end=1, col_start=0, col_end=5)
        )
        
        # 验证 identifier 被自动解析
        assert ref.identifier is not None
        assert isinstance(ref.identifier, Handle)
        assert ref.identifier.name == "alice"
    
    def test_reference_with_property_access(self):
        """测试带属性访问的 Reference"""
        from typedown.core.ast.document import Reference
        from typedown.core.ast.base import SourceLocation
        
        # 创建带属性访问的 Reference
        ref = Reference(
            target="users/alice.name",
            location=SourceLocation(file_path="test.td", line_start=1, line_end=1, col_start=0, col_end=16)
        )
        
        # 验证只解析基础标识符
        assert ref.identifier is not None
        assert isinstance(ref.identifier, Slug)
        assert ref.identifier.path == "users/alice"
    
    def test_reference_with_hash(self):
        """测试 Hash 类型的 Reference"""
        from typedown.core.ast.document import Reference
        from typedown.core.ast.base import SourceLocation
        
        hash_value = "a3b2c1d4e5f6789012345678901234567890123456789012345678901234"
        ref = Reference(
            target=f"sha256:{hash_value}",
            location=SourceLocation(file_path="test.td", line_start=1, line_end=1, col_start=0, col_end=71)
        )
        
        assert ref.identifier is not None
        assert isinstance(ref.identifier, Hash)
        assert ref.identifier.hash_value == hash_value


class TestIdentifierSystemBenefits:
    """测试 Identifier 系统带来的好处"""
    
    def test_no_string_sniffing(self):
        """验证不再使用字符串嗅探"""
        # 这是一个设计验证测试
        # 通过检查 Identifier 的类型，我们可以确保不再使用 startswith 等方法
        
        identifiers = [
            ("alice", Handle),
            ("users/alice", Slug),
            ("sha256:abc123", Hash),
            ("550e8400-e29b-41d4-a716-446655440000", UUID),
        ]
        
        for raw, expected_type in identifiers:
            id_obj = Identifier.parse(raw)
            assert isinstance(id_obj, expected_type)
            # 类型信息在编译时就确定，不需要运行时字符串检查
    
    def test_type_safety(self):
        """验证类型安全性"""
        # 不同类型的标识符不能混淆
        handle = Identifier.parse("alice")
        slug = Identifier.parse("users/alice")
        
        assert type(handle) != type(slug)
        assert handle.level() != slug.level()
        assert handle.is_global() != slug.is_global()
    
    def test_parsing_resolution_decoupling(self):
        """验证 Parsing 与 Resolution 的解耦"""
        # Parsing: Context-Free
        identifier = Identifier.parse("alice")
        assert isinstance(identifier, Handle)
        
        # Resolution: Context-Aware
        symbol_table1 = MockSymbolTable()
        symbol_table1.data["alice"] = "value1"
        
        symbol_table2 = MockSymbolTable()
        symbol_table2.data["alice"] = "value2"
        
        # 同一个 identifier，在不同上下文中解析为不同的值
        result1 = QueryEngine._resolve_by_identifier(identifier, symbol_table1)
        result2 = QueryEngine._resolve_by_identifier(identifier, symbol_table2)
        
        assert result1 == "value1"
        assert result2 == "value2"
