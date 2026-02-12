"""
Pytest configuration and fixtures for integration tests.

This module provides fixtures for testing the integration between:
- VSCode Extension (TypeScript/LSP Client)
- Python Core (LSP Server via pygls)
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Generator, AsyncGenerator
import socket

from lsprotocol.types import (
    InitializeParams,
    ClientCapabilities,
    TextDocumentClientCapabilities,
    WorkspaceClientCapabilities,
    TextDocumentSyncClientCapabilities,
    CompletionClientCapabilities,
    HoverClientCapabilities,
    DefinitionClientCapabilities,
    DocumentSymbolClientCapabilities,
    SemanticTokensClientCapabilities,
)

from typedown.server.application import TypedownLanguageServer
from typedown.core.compiler import Compiler
from rich.console import Console


# =============================================================================
# LSP Server Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def lsp_server_instance() -> AsyncGenerator[TypedownLanguageServer, None]:
    """
    Create a fresh LSP server instance for testing.
    
    Yields a server that is NOT initialized - tests must call initialize themselves.
    """
    server = TypedownLanguageServer("test-typedown-server", "0.0.1")
    yield server
    # Cleanup
    if server.compiler:
        server.compiler = None


@pytest.fixture
def client_capabilities() -> ClientCapabilities:
    """Standard client capabilities for testing."""
    return ClientCapabilities(
        text_document=TextDocumentClientCapabilities(
            synchronization=TextDocumentSyncClientCapabilities(
                dynamic_registration=False,
                will_save=True,
                will_save_wait_until=True,
                did_save=True,
            ),
            completion=CompletionClientCapabilities(
                dynamic_registration=False,
                completion_item={
                    "snippetSupport": True,
                    "commitCharactersSupport": True,
                    "documentationFormat": ["markdown", "plaintext"],
                    "deprecatedSupport": True,
                    "preselectSupport": True,
                },
            ),
            hover=HoverClientCapabilities(
                dynamic_registration=False,
                content_format=["markdown", "plaintext"],
            ),
            definition=DefinitionClientCapabilities(
                dynamic_registration=False,
                link_support=True,
            ),
            document_symbol=DocumentSymbolClientCapabilities(
                dynamic_registration=False,
                hierarchical_document_symbol_support=True,
            ),
            semantic_tokens=SemanticTokensClientCapabilities(
                dynamic_registration=False,
                requests={
                    "range": True,
                    "full": {"delta": False},
                },
                token_types=[
                    "namespace", "type", "class", "enum", "interface",
                    "struct", "typeParameter", "parameter", "variable",
                    "property", "enumMember", "event", "function",
                    "method", "macro", "keyword", "modifier", "comment",
                    "string", "number", "regexp", "operator",
                ],
                token_modifiers=[
                    "declaration", "definition", "readonly", "static",
                    "deprecated", "abstract", "async", "modification",
                    "documentation", "defaultLibrary",
                ],
                formats=["relative"],
            ),
        ),
        workspace=WorkspaceClientCapabilities(
            apply_edit=True,
            workspace_edit={"documentChanges": True},
            did_change_configuration={"dynamic_registration": False},
            did_change_watched_files={"dynamic_registration": False},
            workspace_folders=True,
            configuration=True,
        ),
    )


# =============================================================================
# Project Fixtures
# =============================================================================

class IntegrationTestProject:
    """
    Helper class to create and manage integration test projects.
    
    Provides utilities for:
    - Creating Typedown files
    - Managing temporary directories
    - Starting LSP server with the project
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        self.temp_dir = Path(base_dir) if base_dir else Path(tempfile.mkdtemp(prefix="typedown_integration_"))
        self.files: Dict[Path, str] = {}
        self._compiler: Optional[Compiler] = None
        
    def add_file(self, relative_path: str, content: str) -> "IntegrationTestProject":
        """Add a file to the test project."""
        file_path = self.temp_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        self.files[file_path] = content
        return self
    
    def add_model(self, name: str, class_def: str, metadata: Optional[Dict[str, Any]] = None) -> "IntegrationTestProject":
        """Add a model definition file."""
        meta = metadata or {}
        meta_str = "\n".join(f"{k}: {v}" for k, v in meta.items())
        if meta_str:
            meta_str = f"---\n{meta_str}\n---\n\n"
        else:
            meta_str = "---\ntitle: Model {name}\n---\n\n"
            
        content = f'''{meta_str}```model:{name}
{class_def}
```
'''
        return self.add_file(f"models/{name.lower()}.td", content)
    
    def add_entity(self, type_name: str, entity_id: str, data: Dict[str, Any], 
                   title: Optional[str] = None) -> "IntegrationTestProject":
        """Add an entity definition file."""
        import yaml
        yaml_data = yaml.dump(data, allow_unicode=True, sort_keys=False)
        title_str = title or f"Entity {entity_id}"
        content = f'''---
title: {title_str}
---

```entity {type_name}: {entity_id}
{yaml_data}
```
'''
        return self.add_file(f"entities/{entity_id}.td", content)
    
    def add_spec(self, spec_id: str, target: str, code: str, 
                 scope: str = "local") -> "IntegrationTestProject":
        """Add a spec definition file."""
        # Indent code
        indented_code = "\n".join("    " + line for line in code.strip().split("\n"))
        content = f'''---
title: Spec {spec_id}
---

```spec:{spec_id}
@target(type="{target}", scope="{scope}")
def {spec_id}(subject):
{indented_code}
```
'''
        return self.add_file(f"specs/{spec_id}.td", content)
    
    def add_config(self, content: Optional[str] = None) -> "IntegrationTestProject":
        """Add a config.td file."""
        default = '''---
title: Test Config
---

```config python
# Default test config
```
'''
        return self.add_file("config.td", content or default)
    
    def add_markdown(self, relative_path: str, content: str) -> "IntegrationTestProject":
        """Add a plain markdown file."""
        return self.add_file(relative_path, content)
    
    def get_uri(self, relative_path: str) -> str:
        """Get LSP URI for a file."""
        file_path = self.temp_dir / relative_path
        return file_path.as_uri()
    
    def get_path(self) -> Path:
        """Get the project root path."""
        return self.temp_dir
    
    def get_compiler(self, memory_only: bool = False) -> Compiler:
        """Get or create a compiler instance for this project."""
        if self._compiler is None:
            console = Console(quiet=True)
            self._compiler = Compiler(
                target=self.temp_dir,
                console=console,
                memory_only=memory_only
            )
        return self._compiler
    
    def cleanup(self):
        """Clean up the temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


@pytest.fixture
def integration_project() -> Generator[IntegrationTestProject, None, None]:
    """Fixture providing an IntegrationTestProject."""
    project = IntegrationTestProject()
    yield project
    project.cleanup()


@pytest.fixture
def simple_project(integration_project: IntegrationTestProject) -> IntegrationTestProject:
    """Fixture providing a simple project with basic model and entity."""
    (integration_project
        .add_config()
        .add_model("User", '''
name: str
email: str
age: int = 0
''')
        .add_model("Post", '''
title: str
content: str
author: User
''')
        .add_entity("User", "alice", {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30
        })
        .add_entity("User", "bob", {
            "name": "Bob", 
            "email": "bob@example.com"
        }))
    return integration_project


@pytest.fixture
def project_with_spec(integration_project: IntegrationTestProject) -> IntegrationTestProject:
    """Fixture providing a project with validation specs."""
    (integration_project
        .add_config()
        .add_model("Product", '''
name: str
price: float
stock: int
''')
        .add_entity("Product", "laptop", {
            "name": "Gaming Laptop",
            "price": 1999.99,
            "stock": 10
        })
        .add_spec("check_price", "Product", '''
    assert subject.price > 0, "Price must be positive"
    return True
''', scope="global"))
    return integration_project


# =============================================================================
# LSP Client-Server Integration Fixture
# =============================================================================

class LSPClientServerPair:
    """
    Manages a connected LSP client-server pair for integration testing.
    
    Uses pygls's in-memory transport for fast, isolated testing.
    """
    
    def __init__(self, project_path: Path, memory_only: bool = False):
        self.project_path = project_path
        self.memory_only = memory_only
        self.server: Optional[TypedownLanguageServer] = None
        self._client_capabilities: Optional[ClientCapabilities] = None
        
    async def initialize(self, capabilities: ClientCapabilities) -> Dict[str, Any]:
        """Initialize the LSP server."""
        
        self._client_capabilities = capabilities
        self.server = TypedownLanguageServer("test-server", "0.0.1")
        
        params = InitializeParams(
            process_id=None,
            root_uri=self.project_path.as_uri(),
            capabilities=capabilities,
            initialization_options={"mode": "memory" if self.memory_only else "disk"},
        )
        
        # Call initialize feature directly
        from typedown.server.application import initialize
        initialize(self.server, params)
        return {}
    
    async def open_document(self, relative_path: str, content: str, version: int = 1):
        """Simulate opening a document."""
        from lsprotocol.types import (
            DidOpenTextDocumentParams,
            TextDocumentItem,
        )
        
        uri = self.project_path.joinpath(relative_path).as_uri()
        params = DidOpenTextDocumentParams(
            text_document=TextDocumentItem(
                uri=uri,
                language_id="markdown",
                version=version,
                text=content,
            )
        )
        
        # Get the did_open handler and call it
        from typedown.server.application import did_open
        did_open(self.server, params)
    
    async def change_document(self, relative_path: str, content: str, version: int = 2):
        """Simulate changing a document."""
        from lsprotocol.types import (
            DidChangeTextDocumentParams,
            VersionedTextDocumentIdentifier,
            TextDocumentContentChangeWholeDocument,
        )
        
        uri = self.project_path.joinpath(relative_path).as_uri()
        params = DidChangeTextDocumentParams(
            text_document=VersionedTextDocumentIdentifier(
                uri=uri,
                version=version,
            ),
            content_changes=[
                TextDocumentContentChangeWholeDocument(text=content)
            ],
        )
        
        from typedown.server.application import did_change
        did_change(self.server, params)
    
    async def request_completion(self, relative_path: str, line: int, character: int):
        """Request completions at a position."""
        from lsprotocol.types import (
            CompletionParams,
            TextDocumentIdentifier,
            Position,
        )
        from typedown.server.features.completion import completions
        
        uri = self.project_path.joinpath(relative_path).as_uri()
        params = CompletionParams(
            text_document=TextDocumentIdentifier(uri=uri),
            position=Position(line=line, character=character),
        )
        
        return completions(self.server, params)
    
    async def request_hover(self, relative_path: str, line: int, character: int):
        """Request hover information at a position."""
        from lsprotocol.types import (
            HoverParams,
            TextDocumentIdentifier,
            Position,
        )
        from typedown.server.features.hover import hover
        
        uri = self.project_path.joinpath(relative_path).as_uri()
        params = HoverParams(
            text_document=TextDocumentIdentifier(uri=uri),
            position=Position(line=line, character=character),
        )
        
        return await hover(self.server, params)
    
    async def shutdown(self):
        """Shutdown the server."""
        if self.server:
            from typedown.server.application import shutdown
            shutdown(self.server)


@pytest.fixture
async def lsp_pair(integration_project: IntegrationTestProject, 
                   client_capabilities: ClientCapabilities) -> AsyncGenerator[LSPClientServerPair, None]:
    """
    Fixture providing a connected LSP client-server pair.
    
    Usage:
        async def test_something(lsp_pair):
            await lsp_pair.initialize(client_capabilities)
            await lsp_pair.open_document("test.md", "# Hello")
            completions = await lsp_pair.request_completion("test.md", 0, 2)
    """
    pair = LSPClientServerPair(integration_project.get_path())
    await pair.initialize(client_capabilities)
    yield pair
    await pair.shutdown()


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def wait_for_diagnostics():
    """Utility to wait for diagnostics to be published."""
    async def _wait(duration: float = 0.6):
        """Wait for diagnostics debounce period (default 500ms + buffer)."""
        await asyncio.sleep(duration)
    return _wait


@pytest.fixture
def find_free_port():
    """Find a free port for TCP testing."""
    def _find():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    return _find
