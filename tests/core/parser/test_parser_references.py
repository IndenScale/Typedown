
import pytest
from pathlib import Path
from typedown.core.parser.typedown_parser import TypedownParser
from typedown.core.ast import EntityBlock, Reference

class TestParserReferences:
    def test_entity_block_references(self, tmp_path):
        content = """
```entity User: alice
manager: [[bob]]
friends:
  - [[charlie]]
```
"""
        f = tmp_path / "test.td"
        f.write_text(content, encoding="utf-8")
        
        parser = TypedownParser()
        doc = parser.parse(f)
        
        assert len(doc.entities) == 1
        alice = doc.entities[0]
        
        # Check that references are attached to the block
        assert len(alice.references) == 2
        targets = {ref.target for ref in alice.references}
        assert "bob" in targets
        assert "charlie" in targets
        
        # Check global references also populated
        assert len(doc.references) == 2
    
    def test_multiline_reference_indices(self, tmp_path):
        """
        Scenario from legacy debug_ref_calc.py: Verify line/col calculation 
        for references on multiple lines.
        """
        content = """# Title
Line 2
[[ref1]] and [[ref2]]
Next Line
  [[ref3]]
"""
        f = tmp_path / "index_test.td"
        f.write_text(content, encoding="utf-8")
        
        parser = TypedownParser()
        doc = parser.parse(f)
        
        # [[ref1]] is on Line 3 (1-indexed)
        # Content before [[ref1]] on Line 3 is empty string? No, "Line 2\n"
        # Wait, Line 3 content is "[[ref1]] and [[ref2]]"
        
        refs = sorted(doc.references, key=lambda x: x.location.line_start)
        
        # Verification logic from debug_ref_calc
        lines = content.splitlines()
        
        for ref in refs:
             line_content = lines[ref.location.line_start - 1]
             extracted = line_content[ref.location.col_start : ref.location.col_end]
             assert extracted == f"[[{ref.target}]]"
