"""
Typedown Identifier System - 标识符体系

实现文档中定义的三层标识符光谱 (Identifier Spectrum):
- L0: Hash (sha256:...) - 内容寻址，绝对鲁棒
- L1: Handle (alice) - 局部句柄，开发体验优先
- L3: UUID (550e84...) - 全局唯一标识符

核心设计原则：
1. **不要让字符串裸奔**: 将标识符从字符串提升为强类型对象
2. **Parsing 与 Resolution 解耦**: 
   - Parsing (Context-Free): 识别标识符类型
   - Resolution (Context-Aware): 查找标识符指向的实体
3. **类型安全**: 通过类型系统防止混淆不同层级的标识符
"""

import re
import uuid
from abc import ABC, abstractmethod
from typing import Union
from pydantic import BaseModel, Field


class Identifier(BaseModel, ABC):
    """
    抽象基类：表示 Typedown 中的标识符
    
    所有标识符都是 Value Object，具有以下特性：
    - 不可变 (Immutable)
    - 值相等性 (Value Equality)
    - 无副作用 (Side-Effect Free)
    """
    
    raw: str = Field(description="原始字符串表示")
    
    @abstractmethod
    def level(self) -> int:
        """返回标识符在光谱中的层级 (0-3)"""
        pass
    
    @abstractmethod
    def is_global(self) -> bool:
        """是否为全局稳定标识符（可用于 former/derived_from）"""
        pass
    
    def __str__(self) -> str:
        return self.raw
    
    def __hash__(self) -> int:
        return hash((type(self).__name__, self.raw))
    
    @staticmethod
    def parse(raw: str) -> 'Identifier':
        """
        工厂方法：从原始字符串解析为具体的 Identifier 类型
        
        解析规则：
        1. sha256:... -> Hash (L0)
        2. UUID 格式 -> UUID (L3)
        3. 其他 -> Handle (L1)
        
        Args:
            raw: 原始标识符字符串
            
        Returns:
            具体的 Identifier 子类实例
        """
        raw = raw.strip()
        
        # L0: Hash - Content Addressing
        if raw.startswith("sha256:"):
            return Hash(raw=raw, hash_value=raw[7:])
        
        # L3: UUID - Global Unique Identifier
        if _is_uuid(raw):
            return UUID(raw=raw, uuid_value=raw)
        
        # L1: Handle - Local Reference (路径形式已废弃)
        return Handle(raw=raw, name=raw)


class Handle(Identifier):
    """
    L1: 局部句柄 (Local Handle)
    
    特性：
    - 仅在当前文件或目录作用域内有效
    - 开发体验优先，简洁易用
    - 不可用于 former/derived_from（非全局稳定）
    
    示例: alice, user_config, temp_data
    """
    
    name: str = Field(description="句柄名称")
    
    def level(self) -> int:
        return 1
    
    def is_global(self) -> bool:
        return False


class Hash(Identifier):
    """
    L0: 内容哈希 (Content Hash)
    
    特性：
    - 内容寻址，绝对鲁棒
    - 不可变引用，防止篡改
    - 可用于 former/derived_from
    
    示例: sha256:a3b2c1d4e5f6...
    """
    
    hash_value: str = Field(description="SHA256 哈希值（不含前缀）")
    
    def level(self) -> int:
        return 0
    
    def is_global(self) -> bool:
        return True
    
    @property
    def algorithm(self) -> str:
        """返回哈希算法名称"""
        return "sha256"
    
    @property
    def short_hash(self) -> str:
        """返回短哈希（前 8 位）"""
        return self.hash_value[:8]


class UUID(Identifier):
    """
    L3: 全局唯一标识符 (UUID)
    
    特性：
    - 全局唯一，无需中心协调
    - 可用于 former/derived_from
    - 适用于分布式系统
    
    示例: 550e8400-e29b-41d4-a716-446655440000
    """
    
    uuid_value: str = Field(description="UUID 字符串")
    
    def level(self) -> int:
        return 3
    
    def is_global(self) -> bool:
        return True
    
    def as_uuid(self) -> uuid.UUID:
        """转换为 Python UUID 对象"""
        return uuid.UUID(self.uuid_value)


# ============================================================================
# Helper Functions
# ============================================================================

def _is_uuid(s: str) -> bool:
    """检查字符串是否为有效的 UUID 格式"""
    try:
        uuid.UUID(s)
        return True
    except (ValueError, AttributeError):
        return False


# ============================================================================
# Type Aliases
# ============================================================================

AnyIdentifier = Union[Handle, Hash, UUID]
GlobalIdentifier = Union[Hash, UUID]  # 可用于 former/derived_from 的标识符
