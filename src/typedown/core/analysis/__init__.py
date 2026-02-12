"""
Typedown Core Analysis Module

Provides compilation stages:
- L1: Scanner - Parse documents into AST
- L2: Linker - Build symbol tables and resolve scope
- L2.5: Schema Check - Validate entity structure
- L3: Validator - Resolve references and validate data
- L4: Spec Executor - Run validation specs
"""

from typedown.core.analysis.scanner import Scanner
from typedown.core.analysis.linker import Linker
from typedown.core.analysis.validator import Validator

__all__ = [
    "Scanner",
    "Linker", 
    "Validator",
]
