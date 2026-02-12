"""
Services: Core business logic services for Typedown.

This module contains all service classes that were extracted from the Compiler God Class
to follow the Single Responsibility Principle (SRP).

Architecture:
    Compiler (Facade/Coordinator)
    ├── PipelineService      # Compilation pipeline orchestration
    ├── ValidationService    # L1/L2/L3 validation
    ├── TestService          # L4 Specs + Oracles
    ├── QueryService         # Query interface
    └── SourceService        # Source file management
"""

from .source_service import SourceService
from .validation_service import ValidationService
from .test_service import TestService
from .query_service import QueryService

__all__ = [
    "SourceService",
    "ValidationService", 
    "TestService",
    "QueryService",
]
