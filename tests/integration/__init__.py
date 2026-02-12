"""
Integration tests for Typedown.

This package contains tests that verify the integration between:
- VSCode Extension (TypeScript/LSP Client)
- Python Core (LSP Server)

Test Categories:
- test_lsp_server.py: LSP protocol and server lifecycle tests
- test_compiler_lsp.py: Compiler and LSP integration tests  
- test_e2e_scenarios.py: End-to-end user workflow tests
- test_vscode_extension.py: VSCode extension behavior tests

Usage:
    pytest tests/integration/ -v
    
Requirements:
    - pytest-asyncio
    - pygls (for LSP server)
    - All regular typedown dependencies
"""

__version__ = "0.1.0"
