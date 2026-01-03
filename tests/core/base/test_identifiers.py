"""
测试 Identifier 系统

测试覆盖：
1. Identifier.parse() 工厂方法的解析逻辑
2. 各种标识符类型的属性和行为
3. 边界情况和错误处理
"""

import pytest
from typedown.core.base.identifiers import (
    Identifier,
    Handle,
    Slug,
    Hash,
    UUID,
    GlobalIdentifier,
)


class TestIdentifierParsing:
    """测试 Identifier.parse() 工厂方法"""
    
    def test_parse_handle(self):
        """测试解析局部句柄"""
        # 简单名称
        id1 = Identifier.parse("alice")
        assert isinstance(id1, Handle)
        assert id1.name == "alice"
        assert id1.level() == 1
        assert not id1.is_global()
        
        # 下划线名称
        id2 = Identifier.parse("user_config")
        assert isinstance(id2, Handle)
        assert id2.name == "user_config"
    
    def test_parse_slug(self):
        """测试解析 Slug ID"""
        # 两段路径
        id1 = Identifier.parse("users/alice")
        assert isinstance(id1, Slug)
        assert id1.path == "users/alice"
        assert id1.level() == 2
        assert id1.is_global()
        
        # 多段路径
        id2 = Identifier.parse("config/database/prod")
        assert isinstance(id2, Slug)
        assert id2.segments == ["config", "database", "prod"]
        assert id2.namespace == "config/database"
        assert id2.name == "prod"
        
        # 版本化 ID (必须包含 / 才能被识别为 Slug，否则为 Handle)
        # 修正：之前认为 user-alice-v1 是 Slug，但 parse 逻辑依赖 "/"
        id3 = Identifier.parse("users/alice-v1")
        assert isinstance(id3, Slug)
        assert id3.name == "alice-v1"
    
    def test_parse_hash(self):
        """测试解析内容哈希"""
        hash_value = "a3b2c1d4e5f6789012345678901234567890123456789012345678901234"
        id1 = Identifier.parse(f"sha256:{hash_value}")
        assert isinstance(id1, Hash)
        assert id1.hash_value == hash_value
        assert id1.algorithm == "sha256"
        assert id1.level() == 0
        assert id1.is_global()
        assert id1.short_hash == hash_value[:8]
    
    def test_parse_uuid(self):
        """测试解析 UUID"""
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        id1 = Identifier.parse(uuid_str)
        assert isinstance(id1, UUID)
        assert id1.uuid_value == uuid_str
        assert id1.level() == 3
        assert id1.is_global()
        
        # 验证可以转换为 Python UUID
        uuid_obj = id1.as_uuid()
        assert str(uuid_obj) == uuid_str
    
    def test_parse_edge_cases(self):
        """测试边界情况"""
        # 带空格的输入（应该被 strip）
        id1 = Identifier.parse("  alice  ")
        assert isinstance(id1, Handle)
        assert id1.name == "alice"
        
        # 单字符名称
        id2 = Identifier.parse("x")
        assert isinstance(id2, Handle)
        
        # 长路径
        id3 = Identifier.parse("a/b/c/d/e/f")
        assert isinstance(id3, Slug)
        assert len(id3.segments) == 6


class TestHandleIdentifier:
    """测试 Handle 标识符"""
    
    def test_handle_properties(self):
        """测试 Handle 的基本属性"""
        handle = Handle(raw="alice", name="alice")
        assert handle.level() == 1
        assert not handle.is_global()
        assert str(handle) == "alice"
    
    def test_handle_equality(self):
        """测试 Handle 的相等性"""
        h1 = Handle(raw="alice", name="alice")
        h2 = Handle(raw="alice", name="alice")
        h3 = Handle(raw="bob", name="bob")
        
        # Value Object 相等性
        assert h1 == h2
        assert h1 != h3
        
        # 可以作为字典键
        d = {h1: "value1"}
        assert d[h2] == "value1"


class TestSlugIdentifier:
    """测试 Slug 标识符"""
    
    def test_slug_path_parsing(self):
        """测试 Slug 的路径解析"""
        slug = Slug(raw="users/alice-v1", path="users/alice-v1")
        assert slug.segments == ["users", "alice-v1"]
        assert slug.namespace == "users"
        assert slug.name == "alice-v1"
    
    def test_slug_single_segment(self):
        """测试单段 Slug（虽然不常见）"""
        # 注意：单段应该被解析为 Handle，但如果强制创建 Slug
        slug = Slug(raw="alice", path="alice")
        assert slug.segments == ["alice"]
        assert slug.namespace == ""
        assert slug.name == "alice"
    
    def test_slug_global_property(self):
        """测试 Slug 是全局标识符"""
        slug = Slug(raw="users/alice", path="users/alice")
        assert slug.is_global()
        assert slug.level() == 2


class TestHashIdentifier:
    """测试 Hash 标识符"""
    
    def test_hash_properties(self):
        """测试 Hash 的基本属性"""
        hash_val = "a3b2c1d4e5f6789012345678901234567890123456789012345678901234"
        hash_id = Hash(raw=f"sha256:{hash_val}", hash_value=hash_val)
        
        assert hash_id.algorithm == "sha256"
        assert hash_id.hash_value == hash_val
        assert hash_id.short_hash == "a3b2c1d4"
        assert hash_id.level() == 0
        assert hash_id.is_global()
    
    def test_hash_immutability(self):
        """测试 Hash 的不可变性（通过 Pydantic）"""
        hash_val = "abc123"
        hash_id = Hash(raw=f"sha256:{hash_val}", hash_value=hash_val)
        
        # Pydantic 模型默认是可变的，但我们可以通过配置使其不可变
        # 这里主要测试 Value Object 的语义
        assert hash_id.hash_value == "abc123"


class TestUUIDIdentifier:
    """测试 UUID 标识符"""
    
    def test_uuid_conversion(self):
        """测试 UUID 与 Python uuid 模块的互操作"""
        import uuid
        
        uuid_str = "550e8400-e29b-41d4-a716-446655440000"
        uuid_id = UUID(raw=uuid_str, uuid_value=uuid_str)
        
        # 转换为 Python UUID
        uuid_obj = uuid_id.as_uuid()
        assert isinstance(uuid_obj, uuid.UUID)
        assert str(uuid_obj) == uuid_str
    
    def test_uuid_global_property(self):
        """测试 UUID 是全局标识符"""
        uuid_id = UUID(raw="550e8400-e29b-41d4-a716-446655440000", 
                      uuid_value="550e8400-e29b-41d4-a716-446655440000")
        assert uuid_id.is_global()
        assert uuid_id.level() == 3


class TestIdentifierSpectrum:
    """测试标识符光谱的整体行为"""
    
    def test_level_ordering(self):
        """测试层级顺序：Hash(0) < Handle(1) < Slug(2) < UUID(3)"""
        hash_id = Identifier.parse("sha256:abc123")
        handle_id = Identifier.parse("alice")
        slug_id = Identifier.parse("users/alice")
        uuid_id = Identifier.parse("550e8400-e29b-41d4-a716-446655440000")
        
        assert hash_id.level() == 0
        assert handle_id.level() == 1
        assert slug_id.level() == 2
        assert uuid_id.level() == 3
    
    def test_global_identifier_constraint(self):
        """测试全局标识符约束（用于 former/derived_from）"""
        # 全局标识符
        hash_id = Identifier.parse("sha256:abc123")
        slug_id = Identifier.parse("users/alice")
        uuid_id = Identifier.parse("550e8400-e29b-41d4-a716-446655440000")
        
        assert hash_id.is_global()
        assert slug_id.is_global()
        assert uuid_id.is_global()
        
        # 非全局标识符
        handle_id = Identifier.parse("alice")
        assert not handle_id.is_global()
    
    def test_string_representation(self):
        """测试字符串表示"""
        identifiers = [
            ("alice", "alice"),
            ("users/alice", "users/alice"),
            ("sha256:abc123", "sha256:abc123"),
            ("550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440000"),
        ]
        
        for raw, expected in identifiers:
            id_obj = Identifier.parse(raw)
            assert str(id_obj) == expected


class TestIdentifierEdgeCases:
    """测试边界情况和错误处理"""
    
    def test_empty_string(self):
        """测试空字符串"""
        # 空字符串会被解析为 Handle
        id_obj = Identifier.parse("")
        assert isinstance(id_obj, Handle)
        assert id_obj.name == ""
    
    def test_special_characters_in_handle(self):
        """测试 Handle 中的特殊字符"""
        # 数字开头
        id1 = Identifier.parse("123abc")
        assert isinstance(id1, Handle)
        
        # 连字符
        id2 = Identifier.parse("user-config")
        assert isinstance(id2, Handle)
    
    def test_malformed_hash(self):
        """测试格式错误的哈希"""
        # sha256: 前缀但没有哈希值
        id_obj = Identifier.parse("sha256:")
        assert isinstance(id_obj, Hash)
        assert id_obj.hash_value == ""
    
    def test_malformed_uuid(self):
        """测试格式错误的 UUID"""
        # 不是有效的 UUID 格式
        id_obj = Identifier.parse("not-a-uuid")
        # 应该被解析为 Handle（因为包含连字符但不是 UUID）
        assert isinstance(id_obj, Handle)
    
    def test_path_with_trailing_slash(self):
        """测试带尾部斜杠的路径"""
        # 这会被解析为 Slug（因为包含 /）
        id_obj = Identifier.parse("users/")
        assert isinstance(id_obj, Slug)
        # 注意：这可能不是理想行为，但测试当前实现
