import pytest
from unittest.mock import MagicMock
from pathlib import Path
from lsprotocol.types import CodeLensParams, TextDocumentIdentifier, Position
from typedown.server.features.code_lens import code_lens, CMD_RUN_SPEC, CMD_VIEW_FORMER
from typedown.core.ast.base import SourceLocation

class MockLS:
    def __init__(self):
        self.compiler = MagicMock()
        self.workspace = MagicMock()
        self.show_message_log = MagicMock()
        self.window_show_message = MagicMock()
        self.is_ready = True

def test_code_lens_no_document():
    ls = MockLS()
    # Ensure documents dict is empty or doesn't contain the file
    ls.compiler.documents = {}
    
    params = CodeLensParams(
        text_document=TextDocumentIdentifier(uri="file:///test.td")
    )
    
    result = code_lens(ls, params)
    assert result == []

def test_code_lens_specs():
    ls = MockLS()
    path_str = "/test.td"
    path_obj = Path(path_str)
    uri = "file://" + path_str
    
    # Mock Document
    doc = MagicMock()
    
    # Mock Spec
    spec = MagicMock()
    spec.id = "spec_1"
    spec.location = SourceLocation(file_path=path_str, line_start=10, line_end=12)
    
    doc.specs = [spec]
    doc.entities = []
    
    ls.compiler.documents = {path_obj: doc}
    
    params = CodeLensParams(
        text_document=TextDocumentIdentifier(uri=uri)
    )
    
    result = code_lens(ls, params)
    
    assert len(result) == 1
    lens = result[0]
    assert lens.command.title == "▶ Run Spec"
    assert lens.command.command == CMD_RUN_SPEC
    
    # Check arguments
    # Arguments are passed as a list. Code Lens expects [SpecCommandArgs().model_dump()]
    args = lens.command.arguments
    assert len(args) == 1
    arg_dict = args[0]
    assert arg_dict['file_path'] == str(path_obj)
    assert arg_dict['spec_id'] == "spec_1"
    
    # Check Range (should be line_start - 1)
    # line_start is 10 (1-based from SourceLocation usually? Wait, let's check SourceLocation)
    # If SourceLocation is 1-based, then Position should be 0-based.
    # In code_lens.py: line=max(0, spec.location.line_start - 1)
    # Usually SourceLocation in Typedown is 1-based line numbers? 
    # Let's verify SourceLocation behavior or just trust the logic for now.
    # If line_start=10, then Position line should be 9.
    assert lens.range.start.line == 9

def test_code_lens_entities_with_former():
    ls = MockLS()
    path_str = "/test.td"
    path_obj = Path(path_str)
    uri = "file://" + path_str
    
    doc = MagicMock()
    
    # Mock Entity with former_ids
    entity = MagicMock()
    entity.id = "entity_1"
    entity.location = SourceLocation(file_path=path_str, line_start=20, line_end=22)
    entity.former_ids = ["old_entity_1"]
    
    doc.specs = []
    doc.entities = [entity]
    
    ls.compiler.documents = {path_obj: doc}
    
    params = CodeLensParams(
        text_document=TextDocumentIdentifier(uri=uri)
    )
    
    result = code_lens(ls, params)
    
    assert len(result) == 1
    lens = result[0]
    assert lens.command.title == "📜 View Evolution"
    assert lens.command.command == CMD_VIEW_FORMER
    
    args = lens.command.arguments
    assert len(args) == 1
    arg_dict = args[0]
    assert arg_dict['file_path'] == str(path_obj)
    assert arg_dict['entity_id'] == "entity_1"
    
    assert lens.range.start.line == 19

def test_code_lens_entities_without_former():
    ls = MockLS()
    path_str = "/test.td"
    path_obj = Path(path_str)
    uri = "file://" + path_str
    
    doc = MagicMock()
    
    # Mock Entity WITHOUT former_ids
    entity = MagicMock()
    entity.id = "entity_2"
    entity.location = SourceLocation(file_path=path_str, line_start=30, line_end=32)
    entity.former_ids = [] # Empty
    
    doc.specs = []
    doc.entities = [entity]
    
    ls.compiler.documents = {path_obj: doc}
    
    params = CodeLensParams(
        text_document=TextDocumentIdentifier(uri=uri)
    )
    
    result = code_lens(ls, params)
    
    # Should be empty because no former_ids
    assert len(result) == 0

def test_run_spec_command_logs_output():
    from typedown.server.features.code_lens import run_spec_command
    
    ls = MockLS()
    ls.lock = MagicMock()
    ls.lock.__enter__.return_value = None
    
    # Mock verify_specs to write to the passed console
    def side_effect(spec_filter=None, console=None):
        if console:
            console.print("Mock Spec Output")
        return True
    
    ls.compiler.verify_specs.side_effect = side_effect
    
    # Args: [{'file_path': '...', 'spec_id': '...'}]
    args = [{'file_path': '/test.td', 'spec_id': 'spec_1'}]
    
    run_spec_command(ls, args)
    
    # Check if show_message_log was called with the output
    assert ls.show_message_log.called
    call_args = ls.show_message_log.call_args[0]
    assert "Mock Spec Output" in call_args[0]
    assert "spec_1" in call_args[0]
