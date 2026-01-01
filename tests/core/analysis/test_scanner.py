import pytest
import os
from pathlib import Path
from rich.console import Console
from typedown.core.analysis.scanner import Scanner
from typedown.core.base.config import ScriptConfig

def test_scanner_single_file(tmp_path):
    f = tmp_path / "test.td"
    f.write_text("```model:User\nclass User(BaseModel): pass\n```")
    
    scanner = Scanner(tmp_path, Console())
    docs, targets = scanner.scan(f)
    
    assert f in docs
    assert f in targets
    assert len(docs[f].models) == 1

def test_scanner_directory(tmp_path):
    (tmp_path / "dir1").mkdir()
    f1 = tmp_path / "dir1/a.md"
    f1.write_text("# Hello")
    f2 = tmp_path / "b.td"
    f2.write_text("# World")
    f3 = tmp_path / "ignore.txt"
    f3.write_text("noise")
    
    scanner = Scanner(tmp_path, Console())
    docs, targets = scanner.scan(tmp_path)
    
    assert f1 in docs
    assert f2 in docs
    assert f3 not in docs

def test_scanner_script_filter(tmp_path):
    f1 = tmp_path / "src/a.td"
    f1.parent.mkdir()
    f1.write_text("A")
    f2 = tmp_path / "tests/b.td"
    f2.parent.mkdir()
    f2.write_text("B")
    
    scanner = Scanner(tmp_path, Console())
    
    # Only include src
    script = ScriptConfig(include=["src/**"])
    docs, targets = scanner.scan(tmp_path, script=script)
    
    # Both are scanned (for dependencies), but only targets contains f1
    assert f1 in docs
    assert f2 in docs
    assert f1 in targets
    assert f2 not in targets
    
    # Strict mode: only matching files are scanned
    script_strict = ScriptConfig(include=["src/**"], strict=True)
    docs_s, targets_s = scanner.scan(tmp_path, script=script_strict)
    assert f1 in docs_s
    assert f2 not in docs_s
    assert f1 in targets_s
