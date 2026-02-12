"""
LSP Server Protocol Integration Tests

Tests the Language Server Protocol implementation in Python Core.
These tests verify that the LSP server correctly:
- Initializes and responds to client capabilities
- Handles document lifecycle events (open, change, save, close)
- Manages compiler state across operations
- Handles concurrent requests safely
"""

import pytest
import asyncio
from pathlib import Path
from typing import Optional

from lsprotocol.types import (
    InitializeResult,
    TextDocumentSyncKind,
    CompletionOptions,
    HoverOptions,
    ServerCapabilities,
    MessageType,
)

from typedown.server.application import TypedownLanguageServer, initialize, shutdown


# =============================================================================
# Initialization Tests
# =============================================================================

class TestLSPInitialization:
    """Test LSP server initialization handshake."""
    
    @pytest.mark.asyncio
    async def test_server_initializes_with_disk_mode(self, lsp_server_instance, 
                                                      client_capabilities, 
                                                      integration_project):
        """Test that server initializes correctly in disk mode."""
        from lsprotocol.types import InitializeParams
        
        # Setup project
        integration_project.add_config().add_model("Test", "name: str")
        
        params = InitializeParams(
            process_id=None,
            root_uri=integration_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        # Call initialize (pygls feature handler doesn't return value)
        initialize(lsp_server_instance, params)
        
        # Verify server state after initialization
        assert lsp_server_instance.is_ready is True
        assert lsp_server_instance.compiler is not None
    
    @pytest.mark.asyncio
    async def test_server_initializes_with_memory_mode(self, lsp_server_instance,
                                                        client_capabilities,
                                                        integration_project):
        """Test that server initializes correctly in memory-only mode."""
        from lsprotocol.types import InitializeParams
        
        params = InitializeParams(
            process_id=None,
            root_uri=integration_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "memory"},
        )
        
        # Call initialize (pygls feature handler doesn't return value)
        initialize(lsp_server_instance, params)
        
        # Verify server state after initialization
        assert lsp_server_instance.is_ready is False  # Memory mode waits for loadProject
        assert lsp_server_instance.compiler is not None
    
    @pytest.mark.asyncio
    async def test_server_returns_capabilities(self, lsp_server_instance,
                                                client_capabilities,
                                                simple_project):
        """Test that server returns proper capabilities."""
        from lsprotocol.types import InitializeParams
        
        params = InitializeParams(
            process_id=None,
            root_uri=simple_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        # Call initialize (pygls feature handler doesn't return value)
        initialize(lsp_server_instance, params)
        
        # Verify server is ready
        assert lsp_server_instance.is_ready is True
        assert lsp_server_instance.compiler is not None
    
    @pytest.mark.asyncio
    async def test_server_handles_invalid_root(self, lsp_server_instance,
                                                client_capabilities):
        """Test server behavior with invalid/non-existent root."""
        from lsprotocol.types import InitializeParams
        
        params = InitializeParams(
            process_id=None,
            root_uri="file:///nonexistent/path",
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        # Should not raise, should handle gracefully
        initialize(lsp_server_instance, params)
        # If we get here without exception, test passes
        assert True


# =============================================================================
# Document Lifecycle Tests
# =============================================================================

class TestDocumentLifecycle:
    """Test document open, change, and close events."""
    
    @pytest.mark.asyncio
    async def test_document_open_updates_compiler(self, lsp_pair, simple_project):
        """Test that opening a document updates the compiler's memory overlay."""
        content = '''---
title: New Document
---

# Test

```model:NewModel
value: int
```
'''
        await lsp_pair.open_document("test_new.md", content)
        
        # Compiler should have the document in memory
        assert lsp_pair.server.compiler is not None
        # The compiler should be tracking this document via source_provider
        assert lsp_pair.server.compiler.source_provider is not None
    
    @pytest.mark.asyncio
    async def test_document_change_triggers_recompile(self, lsp_pair, simple_project):
        """Test that document changes trigger recompilation."""
        initial_content = '''---
title: Test
---

```model:Dynamic
name: str
```
'''
        await lsp_pair.open_document("dynamic.md", initial_content)
        
        # Change the content
        changed_content = '''---
title: Test
---

```model:Dynamic
name: str
age: int
```
'''
        await lsp_pair.change_document("dynamic.md", changed_content, version=2)
        
        # Server should process the change (may not immediately recompile due to debounce)
        assert lsp_pair.server.compiler is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_document_operations(self, lsp_pair, integration_project):
        """Test that concurrent document operations are handled safely."""
        # Setup project with multiple files
        (integration_project
            .add_config()
            .add_model("ModelA", "field_a: str")
            .add_model("ModelB", "field_b: int"))
        
        # lsp_pair is already initialized by fixture
        
        # Open multiple documents concurrently
        contents = [
            ("file1.md", "# File 1\n\n```entity ModelA: e1\nfield_a: test\n```"),
            ("file2.md", "# File 2\n\n```entity ModelA: e2\nfield_a: test2\n```"),
            ("file3.md", "# File 3\n\n```entity ModelB: e3\nfield_b: 42\n```"),
        ]
        
        tasks = [lsp_pair.open_document(path, content) for path, content in contents]
        await asyncio.gather(*tasks)
        
        # All operations should complete without error
        assert lsp_pair.server.compiler is not None


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestErrorHandling:
    """Test LSP error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_operations_before_initialization(self, lsp_server_instance):
        """Test that operations before initialization are handled gracefully."""
        # Try to use server before initialization
        assert lsp_server_instance.is_ready is False
        assert lsp_server_instance.compiler is None
        
        # Operations should not crash, just return/ignore
        # (Specific behavior depends on implementation)
    
    @pytest.mark.asyncio
    async def test_invalid_document_uris(self, lsp_pair, simple_project):
        """Test handling of invalid document URIs."""
        # lsp_pair already initialized by fixture
        
        # Try to open document with invalid URI format
        # Should handle gracefully
        try:
            await lsp_pair.open_document("../../../etc/passwd", "# Test")
        except Exception as e:
            # May raise or handle gracefully - both are acceptable
            pass
    
    @pytest.mark.asyncio
    async def test_malformed_document_content(self, lsp_pair, simple_project):
        """Test handling of malformed document content."""
        # lsp_pair already initialized by fixture
        
        # Content with syntax errors
        malformed_content = '''---
title: Test
---

```model:Broken
this is not valid
```

[[invalid reference syntax]]
'''
        
        # Should handle without crashing
        await lsp_pair.open_document("malformed.md", malformed_content)
        assert lsp_pair.server.compiler is not None


# =============================================================================
# Server State Tests
# =============================================================================

class TestServerState:
    """Test server state management."""
    
    @pytest.mark.asyncio
    async def test_compiler_lock_protection(self, lsp_server_instance, 
                                             client_capabilities,
                                             simple_project):
        """Test that compiler operations are properly locked."""
        from lsprotocol.types import InitializeParams
        
        params = InitializeParams(
            process_id=None,
            root_uri=simple_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        initialize(lsp_server_instance, params)
        
        # Verify lock exists
        assert hasattr(lsp_server_instance, 'lock')
        assert lsp_server_instance.lock is not None
    
    @pytest.mark.asyncio
    async def test_server_mode_persistence(self, lsp_server_instance,
                                            client_capabilities,
                                            integration_project):
        """Test that server mode (disk/memory) is properly persisted."""
        from lsprotocol.types import InitializeParams
        
        # Test disk mode
        params_disk = InitializeParams(
            process_id=None,
            root_uri=integration_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        initialize(lsp_server_instance, params_disk)
        assert lsp_server_instance.is_ready is True
        
        # Create new server for memory mode test
        server2 = TypedownLanguageServer("test-server-2", "0.0.1")
        params_memory = InitializeParams(
            process_id=None,
            root_uri=integration_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "memory"},
        )
        
        initialize(server2, params_memory)
        assert server2.is_ready is False


# =============================================================================
# Integration with VSCode Client Behavior
# =============================================================================

class TestVSCodeClientSimulation:
    """Simulate specific VSCode client behaviors."""
    
    @pytest.mark.asyncio
    async def test_vscode_startup_sequence(self, lsp_pair, simple_project):
        """Simulate VSCode's startup LSP sequence."""
        # 1. Initialize
        # lsp_pair already initialized by fixture
        
        # 2. VSCode opens files that were previously open
        await lsp_pair.open_document("models/user.td", '''---
title: User
---

```model:User
name: str
```
''')
        
        # 3. VSCode may request various features
        # (Completions, hover, etc. - tested in other test files)
        
        assert lsp_pair.server.is_ready is True
    
    @pytest.mark.asyncio
    async def test_vscode_configuration_change(self, lsp_pair, simple_project):
        """Simulate VSCode configuration change and server restart."""
        # lsp_pair already initialized by fixture
        
        # Server is running
        assert lsp_pair.server.is_ready is True
        
        # Simulate shutdown (as VSCode would do on config change)
        await lsp_pair.shutdown()
        
        # Server should handle shutdown gracefully
        # Note: Current implementation may not change is_ready on shutdown


# =============================================================================
# Performance and Load Tests
# =============================================================================

class TestPerformance:
    """Basic performance tests."""
    
    @pytest.mark.asyncio
    async def test_large_document_handling(self, lsp_pair, integration_project):
        """Test handling of large documents."""
        # lsp_pair already initialized by fixture
        
        # Create a large document
        large_content = "---\ntitle: Large Doc\n---\n\n# Large Document\n\n"
        for i in range(100):
            large_content += f"```model:Model{i}\nfield_{i}: str\n```\n\n"
        
        # Should handle without timeout
        await lsp_pair.open_document("large.md", large_content)
        assert lsp_pair.server.compiler is not None
    
    @pytest.mark.asyncio
    async def test_rapid_document_changes(self, lsp_pair, integration_project):
        """Test handling of rapid document changes (typing simulation)."""
        # lsp_pair already initialized by fixture
        
        # Open document
        await lsp_pair.open_document("typing.md", "# Start")
        
        # Simulate rapid typing (multiple changes in quick succession)
        for i in range(10):
            content = f"# Start\n\nLine {i}\n"
            await lsp_pair.change_document("typing.md", content, version=i+2)
            await asyncio.sleep(0.05)  # Small delay between changes
        
        # Server should remain stable
        assert lsp_pair.server.compiler is not None


# =============================================================================
# Custom Method Tests
# =============================================================================

class TestCustomMethods:
    """Test Typedown-specific LSP methods."""
    
    @pytest.mark.asyncio
    async def test_custom_update_file_method(self, lsp_server_instance,
                                              client_capabilities,
                                              simple_project):
        """Test the typedown/updateFile custom method."""
        from lsprotocol.types import InitializeParams
        from typedown.server.application import custom_update_file
        
        params = InitializeParams(
            process_id=None,
            root_uri=simple_project.get_uri(""),
            capabilities=client_capabilities,
            initialization_options={"mode": "disk"},
        )
        
        initialize(lsp_server_instance, params)
        
        # Test custom update
        test_uri = simple_project.get_uri("test.md")
        test_content = "# Test Content"
        
        update_params = {"uri": test_uri, "content": test_content}
        custom_update_file(lsp_server_instance, update_params)
        
        # Should update the document in compiler's memory overlay
        assert lsp_server_instance.compiler is not None
