"""
Typedown Identifier System

Implements the three-level Identifier Spectrum defined in the documentation:
- L0: Hash (sha256:...) - Content addressing, absolutely robust
- L1: Handle (alice) - Local handle, developer experience first
- L3: UUID (550e84...) - Globally unique identifier

Core Design Principles:
1. **No naked strings**: Elevate identifiers from strings to strongly-typed objects
2. **Decouple Parsing from Resolution**:
   - Parsing (Context-Free): Identify identifier type
   - Resolution (Context-Aware): Lookup the entity the identifier points to
3. **Type Safety**: Prevent confusion between different identifier levels via the type system
"""

import uuid
from abc import ABC, abstractmethod
from typing import Union
from pydantic import BaseModel, Field


class Identifier(BaseModel, ABC):
    """
    Abstract base class: Represents an identifier in Typedown.
    
    All identifiers are Value Objects with the following characteristics:
    - Immutable
    - Value Equality
    - Side-Effect Free
    """
    
    raw: str = Field(description="Raw string representation")
    
    @abstractmethod
    def level(self) -> int:
        """Returns the level of the identifier in the spectrum (0-3)."""
        pass
    
    @abstractmethod
    def is_global(self) -> bool:
        """Whether this is a globally stable identifier (can be used for former/derived_from)."""
        pass
    
    def __str__(self) -> str:
        return self.raw
    
    def __hash__(self) -> int:
        return hash((type(self).__name__, self.raw))
    
    @staticmethod
    def parse(raw: str) -> 'Identifier':
        """
        Factory method: Parse a raw string into a concrete Identifier type.
        
        Parsing rules:
        1. sha256:... -> Hash (L0)
        2. UUID format -> UUID (L3)
        3. Others -> Handle (L1)
        
        Args:
            raw: Raw identifier string
            
        Returns:
            An instance of a concrete Identifier subclass
        """
        raw = raw.strip()
        
        # L0: Hash - Content Addressing
        if raw.startswith("sha256:"):
            return Hash(raw=raw, hash_value=raw[7:])
        
        # L3: UUID - Global Unique Identifier
        if _is_uuid(raw):
            return UUID(raw=raw, uuid_value=raw)
        
        # L1: Handle - Local Reference (path format is deprecated)
        return Handle(raw=raw, name=raw)


class Handle(Identifier):
    """
    L1: Local Handle
    
    Characteristics:
    - Only valid within the current file or directory scope
    - Developer experience first, simple and easy to use
    - Cannot be used for former/derived_from (not globally stable)
    
    Examples: alice, user_config, temp_data
    """
    
    name: str = Field(description="Handle name")
    
    def level(self) -> int:
        return 1
    
    def is_global(self) -> bool:
        return False


class Hash(Identifier):
    """
    L0: Content Hash
    
    Characteristics:
    - Content addressing, absolutely robust
    - Immutable reference, tamper-proof
    - Can be used for former/derived_from
    
    Examples: sha256:a3b2c1d4e5f6...
    """
    
    hash_value: str = Field(description="SHA256 hash value (without prefix)")
    
    def level(self) -> int:
        return 0
    
    def is_global(self) -> bool:
        return True
    
    @property
    def algorithm(self) -> str:
        """Returns the hash algorithm name."""
        return "sha256"
    
    @property
    def short_hash(self) -> str:
        """Returns the short hash (first 8 characters)."""
        return self.hash_value[:8]


class UUID(Identifier):
    """
    L3: Universally Unique Identifier (UUID)
    
    Characteristics:
    - Globally unique without central coordination
    - Can be used for former/derived_from
    - Suitable for distributed systems
    
    Examples: 550e8400-e29b-41d4-a716-446655440000
    """
    
    uuid_value: str = Field(description="UUID string")
    
    def level(self) -> int:
        return 3
    
    def is_global(self) -> bool:
        return True
    
    def as_uuid(self) -> uuid.UUID:
        """Convert to Python UUID object."""
        return uuid.UUID(self.uuid_value)


# ============================================================================
# Helper Functions
# ============================================================================

def _is_uuid(s: str) -> bool:
    """Check if the string is a valid UUID format."""
    try:
        uuid.UUID(s)
        return True
    except (ValueError, AttributeError):
        return False


# ============================================================================
# Type Aliases
# ============================================================================

AnyIdentifier = Union[Handle, Hash, UUID]
GlobalIdentifier = Union[Hash, UUID]  # Identifiers that can be used for former/derived_from
