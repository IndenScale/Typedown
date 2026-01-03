
import pytest
from typedown.core.parser.typedown_parser import TypedownParser

def test_strict_identity_valid():
    """验证合法的 Signature Identity 不会报错"""
    parser = TypedownParser()
    content = """
```entity User: alice
name: "Alice"
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.entities) == 1
    assert doc.entities[0].id == "alice"

def test_strict_identity_rejects_body_id():
    """验证当 Body 中包含 id 时，解析器抛出异常"""
    parser = TypedownParser()
    content = """
```entity User: alice
id: "duplicate-id"
name: "Alice"
```
"""
    # 期望抛出 ValueError，且信息包含特定关键词
    with pytest.raises(ValueError, match="Conflict: System ID must be defined in Block Signature"):
        parser.parse_text(content, "test.td")

def test_strict_identity_allows_uuid_in_body():
    """验证 uuid 字段仍然允许在 body 中（它是 L3 辅助 ID，不冲突）"""
    parser = TypedownParser()
    content = """
```entity User: alice
uuid: "550e8400-e29b-41d4-a716-446655440000"
name: "Alice"
```
"""
    doc = parser.parse_text(content, "test.td")
    assert len(doc.entities) == 1
    assert doc.entities[0].id == "alice"
    assert doc.entities[0].raw_data["uuid"] == "550e8400-e29b-41d4-a716-446655440000"
