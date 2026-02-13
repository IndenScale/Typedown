"""
Typedown Identifier System

Implements the two-type reference system:
- Hash (sha256:...) - Content addressing, immutable reference, globally stable
- ID - Local identifier, scoped reference, developer experience first

Core Design Principles:
1. **No naked strings**: Elevate identifiers from strings to strongly-typed objects
2. **Decouple Parsing from Resolution**:
   - Parsing (Context-Free): Identify identifier type
   - Resolution (Context-Aware): Lookup the entity the identifier points to
3. **Type Safety**: Prevent confusion between different identifier types via the type system
"""

from abc import ABC
from enum import Enum, auto
from typing import Union
from pydantic import BaseModel, Field


class ReferenceType(Enum):
    """Enumeration of reference types in Typedown."""
    ID = auto()      # Local scoped identifier
    HASH = auto()    # Content hash for immutable addressing


class Identifier(BaseModel, ABC):
    """
    Abstract base class: Represents an identifier in Typedown.
    
    All identifiers are Value Objects with the following characteristics:
    - Immutable
    - Value Equality
    - Side-Effect Free
    """
    
    raw: str = Field(description="Raw string representation")
    
    @property
    def ref_type(self) -> ReferenceType:
        """Returns the type of this reference."""
        raise NotImplementedError
    
    def __str__(self) -> str:
        return self.raw
    
    def __hash__(self) -> int:
        return hash((type(self).__name__, self.raw))
    
    @staticmethod
    def parse(raw: str) -> 'Identifier':
        """
        Factory method: Parse a raw string into a concrete Identifier type.
        
        Parsing rules:
        1. sha256:... -> Hash
        2. Others -> ID
        
        Args:
            raw: Raw identifier string
            
        Returns:
            An instance of a concrete Identifier subclass
        """
        raw = raw.strip()
        
        if raw.startswith("sha256:"):
            return Hash(raw=raw, hash_value=raw[7:])
        
        return ID(raw=raw, name=raw)


class ID(Identifier):
    """
    Local identifier for scoped references.
    
    Characteristics:
    - Only valid within the current file or directory scope
    - Developer experience first, simple and easy to use
    - Cannot be used for former/derived_from (not globally stable)
    
    Examples: alice, user_config, temp_data, user-alice-v1
    """
    
    name: str = Field(description="ID name")
    
    @property
    def ref_type(self) -> ReferenceType:
        return ReferenceType.ID


class Hash(Identifier):
    """
    Content Hash for immutable content addressing.
    
    Characteristics:
    - Content addressing, absolutely robust
    - Immutable reference, tamper-proof
    - Can be used for former/derived_from
    
    Examples: sha256:a3b2c1d4e5f6...
    """
    
    hash_value: str = Field(description="SHA256 hash value (without prefix)")
    
    @property
    def ref_type(self) -> ReferenceType:
        return ReferenceType.HASH
    
    @property
    def algorithm(self) -> str:
        """Returns the hash algorithm name."""
        return "sha256"
    
    @property
    def short_hash(self) -> str:
        """Returns the short hash (first 8 characters)."""
        return self.hash_value[:8]


# ============================================================================
# Type Aliases
# ============================================================================

AnyIdentifier = Union[ID, Hash]
