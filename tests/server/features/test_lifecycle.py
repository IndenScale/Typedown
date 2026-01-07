import pytest
from unittest.mock import MagicMock, patch
from lsprotocol.types import InitializeParams
from typedown.server.application import initialize, TypedownLanguageServer
from pathlib import Path

class MockLS(TypedownLanguageServer):
    def __init__(self):
        # We don't call super().__init__ to avoid full pygls setup overhead in mocks
        self.compiler = None
        self.is_ready = False
        self.show_message_log = MagicMock()
        self.window_log_message = MagicMock()

def test_initialize_default_disk_mode():
    ls = MockLS()
    params = InitializeParams(
        process_id=1234,
        root_uri="file:///test/project",
        capabilities=MagicMock(),
        initialization_options=None # Default
    )
    
    with patch("typedown.server.application.Compiler") as MockCompiler:
        mock_compiler_instance = MockCompiler.return_value
        
        initialize(ls, params)
        
        # Verify Compiler initialized with memory_only=False
        MockCompiler.assert_called_once()
        call_kwargs = MockCompiler.call_args[1]
        assert call_kwargs["memory_only"] is False
        
        # Verify compile() was called (Disk mode scans)
        mock_compiler_instance.compile.assert_called_once()
        
        # Verify is_ready is True
        assert ls.is_ready is True

def test_initialize_memory_mode_dict():
    ls = MockLS()
    params = InitializeParams(
        process_id=1234,
        root_uri="file:///test/project",
        capabilities=MagicMock(),
        initialization_options={"mode": "memory"}
    )
    
    with patch("typedown.server.application.Compiler") as MockCompiler:
        mock_compiler_instance = MockCompiler.return_value
        
        initialize(ls, params)
        
        # Verify Compiler initialized with memory_only=True
        call_kwargs = MockCompiler.call_args[1]
        assert call_kwargs["memory_only"] is True
        
        # Verify compile() was NOT called
        mock_compiler_instance.compile.assert_not_called()
        
        # Verify is_ready is False (waiting for loadProject)
        assert ls.is_ready is False

def test_initialize_memory_mode_object():
    ls = MockLS()
    # Mock initialization_options as an object with .mode attribute
    opts = MagicMock()
    opts.mode = "memory"
    
    params = InitializeParams(
        process_id=1234,
        root_uri="file:///test/project",
        capabilities=MagicMock(),
        initialization_options=opts
    )
    
    with patch("typedown.server.application.Compiler") as MockCompiler:
        initialize(ls, params)
        
        call_kwargs = MockCompiler.call_args[1]
        assert call_kwargs["memory_only"] is True
        assert ls.is_ready is False
