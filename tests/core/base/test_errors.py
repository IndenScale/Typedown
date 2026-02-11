"""
Tests for Typedown Error System: Error codes and structured reporting.
"""

import pytest
from pathlib import Path
from typedown.core.base.errors import (
    TypedownError, ErrorCode, ErrorLevel,
    CycleError, ReferenceError, QueryError,
    DiagnosticReport, 
    scanner_error, linker_error, validator_error, spec_error,
    ERROR_TEMPLATES
)
from typedown.core.ast.base import SourceLocation


class TestErrorCode:
    """Test ErrorCode enum functionality."""
    
    def test_error_code_format(self):
        """Error codes should follow E{stage}{category}{number} format."""
        assert str(ErrorCode.E0101) == "E0101"
        assert str(ErrorCode.E0221) == "E0221"
        assert str(ErrorCode.E0341) == "E0341"
        assert str(ErrorCode.E0421) == "E0421"
    
    def test_error_code_stage(self):
        """Error codes should report correct stage."""
        assert ErrorCode.E0101.stage == "L1-Scanner"
        assert ErrorCode.E0221.stage == "L2-Linker"
        assert ErrorCode.E0341.stage == "L3-Validator"
        assert ErrorCode.E0421.stage == "L4-Spec"
        assert ErrorCode.E0981.stage == "System"
    
    def test_error_code_category(self):
        """Error codes should report correct category."""
        assert ErrorCode.E0101.category == "Syntax/Parse"
        assert ErrorCode.E0221.category == "Execution"
        assert ErrorCode.E0231.category == "Execution"
        assert ErrorCode.E0361.category == "Schema/Type"
        assert ErrorCode.E0981.category == "System"
    
    def test_error_code_default_level(self):
        """Error codes should have appropriate default severity levels."""
        assert ErrorCode.E0101.default_level == ErrorLevel.ERROR
        assert ErrorCode.E0224.default_level == ErrorLevel.WARNING  # Model rebuild warning


class TestErrorLevel:
    """Test ErrorLevel enum functionality."""
    
    def test_error_level_values(self):
        """Error levels should have correct string values."""
        assert ErrorLevel.ERROR.value == "error"
        assert ErrorLevel.WARNING.value == "warning"
        assert ErrorLevel.INFO.value == "info"
        assert ErrorLevel.HINT.value == "hint"


class TestTypedownError:
    """Test TypedownError base class."""
    
    def test_basic_error_creation(self):
        """Can create basic error with message and code."""
        err = TypedownError(
            message="Test error",
            code=ErrorCode.E0101,
            level=ErrorLevel.ERROR
        )
        assert err.message == "Test error"
        assert err.code == ErrorCode.E0101
        assert err.level == ErrorLevel.ERROR
    
    def test_error_with_location(self):
        """Can create error with source location."""
        loc = SourceLocation(file_path="test.td", line_start=10, line_end=10, col_start=5, col_end=15)
        err = TypedownError(
            message="Syntax error",
            code=ErrorCode.E0101,
            location=loc
        )
        assert err.location == loc
    
    def test_error_to_dict(self):
        """Error can be serialized to dictionary."""
        loc = SourceLocation(file_path="test.td", line_start=10, col_start=5, line_end=10, col_end=15)
        err = TypedownError(
            message="Test error",
            code=ErrorCode.E0101,
            level=ErrorLevel.ERROR,
            location=loc,
            details={"foo": "bar"}
        )
        d = err.to_dict()
        assert d["code"] == "E0101"
        assert d["level"] == "error"
        assert d["message"] == "Test error"
        assert d["stage"] == "L1-Scanner"
        assert d["category"] == "Syntax/Parse"
        assert d["location"]["file_path"] == "test.td"
        assert d["details"]["foo"] == "bar"
    
    def test_legacy_severity_parameter(self):
        """Backward compatibility with 'severity' parameter."""
        err = TypedownError(
            message="Test",
            severity="warning"
        )
        assert err.level == ErrorLevel.WARNING
        assert err.severity == "warning"  # Legacy property
    
    def test_from_template(self):
        """Can create error from template."""
        err = TypedownError.from_template(
            ErrorCode.E0231,
            id="MyModel",
            location=SourceLocation(file_path="test.td", line_start=1, line_end=1, col_start=0, col_end=10)
        )
        assert err.code == ErrorCode.E0231
        assert "MyModel" in err.message
        assert err.location.file_path == "test.td"


class TestSpecializedErrors:
    """Test specialized error subclasses."""
    
    def test_cycle_error(self):
        """CycleError should have correct code."""
        err = CycleError("a -> b -> a")
        assert err.code == ErrorCode.E0342
        assert err.level == ErrorLevel.ERROR
    
    def test_reference_error(self):
        """ReferenceError should have correct code."""
        err = ReferenceError("Unknown ref")
        assert err.code == ErrorCode.E0341
        assert err.level == ErrorLevel.ERROR
    
    def test_query_error(self):
        """QueryError should have correct code."""
        err = QueryError("Invalid syntax")
        assert err.code == ErrorCode.E0365
        assert err.level == ErrorLevel.ERROR


class TestErrorFactoryFunctions:
    """Test error factory helper functions."""
    
    def test_scanner_error(self):
        """scanner_error creates correct error type."""
        err = scanner_error(
            ErrorCode.E0103,
            entity_id="test",
            location=SourceLocation(file_path="test.td", line_start=1, line_end=1, col_start=0, col_end=10)
        )
        assert err.code.stage == "L1-Scanner"
    
    def test_linker_error(self):
        """linker_error creates correct error type."""
        err = linker_error(
            ErrorCode.E0221,
            model_id="TestModel",
            details="Failed to execute"
        )
        assert err.code.stage == "L2-Linker"
    
    def test_validator_error(self):
        """validator_error creates correct error type."""
        err = validator_error(
            ErrorCode.E0361,
            entity="test",
            details="Schema violation"
        )
        assert err.code.stage == "L3-Validator"
    
    def test_spec_error(self):
        """spec_error creates correct error type."""
        err = spec_error(
            ErrorCode.E0421,
            spec_id="test_spec",
            details="Assertion failed"
        )
        assert err.code.stage == "L4-Spec"


class TestDiagnosticReport:
    """Test DiagnosticReport collection class."""
    
    def test_empty_report(self):
        """Empty report has no errors."""
        report = DiagnosticReport()
        assert not report.has_errors()
        assert len(report.errors) == 0
    
    def test_add_error(self):
        """Can add errors to report."""
        report = DiagnosticReport()
        err = TypedownError("Test", code=ErrorCode.E0101)
        report.add(err)
        assert len(report.errors) == 1
        assert report.has_errors()
    
    def test_extend_errors(self):
        """Can extend report with multiple errors."""
        report = DiagnosticReport()
        errors = [
            TypedownError("Error 1", code=ErrorCode.E0101),
            TypedownError("Error 2", code=ErrorCode.E0102)
        ]
        report.extend(errors)
        assert len(report.errors) == 2
    
    def test_filter_by_level(self):
        """Can filter errors by level."""
        report = DiagnosticReport()
        report.add(TypedownError("Error", code=ErrorCode.E0101, level=ErrorLevel.ERROR))
        report.add(TypedownError("Warning", code=ErrorCode.E0224, level=ErrorLevel.WARNING))
        
        errors = report.by_level(ErrorLevel.ERROR)
        assert len(errors) == 1
        assert errors[0].message == "Error"
    
    def test_filter_by_code(self):
        """Can filter errors by code."""
        report = DiagnosticReport()
        report.add(TypedownError("Error 1", code=ErrorCode.E0101))
        report.add(TypedownError("Error 2", code=ErrorCode.E0102))
        
        errors = report.by_code(ErrorCode.E0101)
        assert len(errors) == 1
        assert errors[0].message == "Error 1"
    
    def test_filter_by_stage(self):
        """Can filter errors by stage."""
        report = DiagnosticReport()
        report.add(TypedownError("L1", code=ErrorCode.E0101))
        report.add(TypedownError("L2", code=ErrorCode.E0221))
        
        l1_errors = report.by_stage("L1-Scanner")
        assert len(l1_errors) == 1
    
    def test_to_dict_list(self):
        """Can convert report to list of dicts."""
        report = DiagnosticReport()
        report.add(TypedownError("Test", code=ErrorCode.E0101))
        
        dict_list = report.to_dict_list()
        assert len(dict_list) == 1
        assert dict_list[0]["code"] == "E0101"


class TestErrorTemplates:
    """Test error message templates."""
    
    def test_all_codes_have_templates(self):
        """All error codes should have templates."""
        for code in ErrorCode:
            assert code in ERROR_TEMPLATES, f"Missing template for {code}"
    
    def test_template_formatting(self):
        """Templates should format correctly."""
        err = TypedownError.from_template(
            ErrorCode.E0362,
            field="manager",
            expected="UserAccount",
            value="org-123",
            actual="Organization"
        )
        assert "manager" in err.message
        assert "UserAccount" in err.message
        assert "org-123" in err.message


class TestJSONSerialization:
    """Test JSON serialization of errors."""
    
    def test_error_json_structure(self):
        """Errors serialize to correct JSON structure."""
        import json
        from typedown.commands.utils import json_serializer
        
        err = TypedownError(
            message="Test error",
            code=ErrorCode.E0101,
            level=ErrorLevel.ERROR,
            location=SourceLocation(file_path="test.td", line_start=10, line_end=10, col_start=5, col_end=15)
        )
        
        result = json_serializer(err)
        assert result["code"] == "E0101"
        assert result["level"] == "error"
        assert result["message"] == "Test error"
        assert result["location"]["file_path"] == "test.td"
    
    def test_diagnostic_report_json(self):
        """DiagnosticReport serializes correctly."""
        from typedown.commands.utils import json_serializer
        
        report = DiagnosticReport()
        report.add(TypedownError("Test", code=ErrorCode.E0101))
        
        result = json_serializer(report)
        assert len(result) == 1
        assert result[0]["code"] == "E0101"
