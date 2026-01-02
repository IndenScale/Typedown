
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
