
import pytest
from pathlib import Path
from typedown.core.parser.typedown_parser import TypedownParser
from typedown.core.ast import SpecBlock

class TestSpecValidations:
    def setup_method(self):
        self.parser = TypedownParser()
        self.dummy_path = Path("dummy.td")

    def test_spec_with_space_delimiter(self):
        """Test that 'spec: name' (with space) is parsed correctly."""
        content = """
```spec: my_spec_func
def my_spec_func(subject):
    pass
```
"""
        doc = self.parser.parse_text(content, str(self.dummy_path))
        assert len(doc.specs) == 1
        assert doc.specs[0].id == "my_spec_func"

    def test_spec_id_charset_valid(self):
        """Test strict charset validation for spec ID (alphanumeric + underscore)."""
        # Valid ID
        content = """
```spec: check_valid_123
def check_valid_123(subject):
    pass
```
"""
        doc = self.parser.parse_text(content, str(self.dummy_path))
        assert len(doc.specs) == 1
        assert doc.specs[0].id == "check_valid_123"

    def test_spec_id_charset_invalid_hyphen(self):
        """Test that IDs with hyphens are rejected."""
        content = """
```spec: invalid-id
def invalid_id():
    pass
```
"""
        with pytest.raises(ValueError, match="must be a valid identifier"):
            self.parser.parse_text(content, str(self.dummy_path))

    def test_spec_id_charset_invalid_number_start(self):
        """Test that IDs starting with numbers are rejected."""
        content = """
```spec: 123invalid
def 123invalid():
    pass
```
"""
        with pytest.raises(ValueError, match="must be a valid identifier"):
            # Note: The parser relies on regex ^[a-zA-Z_]\w*$ which excludes number start
            self.parser.parse_text(content, str(self.dummy_path))

    def test_missing_function_definition(self):
        """Test validation ensuring the function matching ID exists."""
        content = """
```spec: my_check
def other_function(subject):
    pass
```
"""
        with pytest.raises(ValueError, match="Spec 'my_check' definition missing"):
            self.parser.parse_text(content, str(self.dummy_path))

    def test_multiple_functions_finds_correct_one(self):
        """Test that having multiple functions is fine as long as the matching one exists."""
        content = """
```spec: real_test
def helper(data):
    return True

def real_test(subject):
    assert helper(subject)
```
"""
        doc = self.parser.parse_text(content, str(self.dummy_path))
        assert len(doc.specs) == 1
        assert doc.specs[0].id == "real_test"
