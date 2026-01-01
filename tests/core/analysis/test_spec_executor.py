
import unittest
from unittest.mock import MagicMock, patch
from typedown.core.analysis.spec_executor import SpecExecutor, TargetSelector
from typedown.core.ast import SpecBlock, EntityBlock, SourceLocation

class TestSpecExecutor(unittest.TestCase):
    def setUp(self):
        self.console = MagicMock()
        self.executor = SpecExecutor(self.console)
        self.location = SourceLocation(file_path="test.td", line_start=1, line_end=1)

    def test_selector_parsing(self):
        # Test type selector
        s1 = TargetSelector('@target(type="User")')
        self.assertEqual(s1.type_filter, "User")
        
        # Test id selector
        s2 = TargetSelector('@target(id="users/alice")')
        self.assertEqual(s2.id_filter, "users/alice")
        
        # Test mixed (though usually one is enough)
        s3 = TargetSelector('@target(type="User", id="alice")')
        self.assertEqual(s3.type_filter, "User")
        self.assertEqual(s3.id_filter, "alice")

    def test_matching_derived_entities(self):
        """
        Verify that entities using `derived_from` are correctly matched 
        if they satisfy the type/id criteria.
        """
        # Entity 1: Base User
        base_user = EntityBlock(
            id="user1", 
            class_name="User", 
            location=self.location,
            raw_data={"name": "Base"}
        )
        
        # Entity 2: Derived User (Same Type)
        derived_user = EntityBlock(
            id="user2", 
            class_name="User", 
            location=self.location,
            derived_from_id="user1",
            raw_data={"name": "Derived"}
        )
        
        # Entity 3: Different Type
        other_user = EntityBlock(
            id="admin1", 
            class_name="Admin", 
            location=self.location,
            raw_data={"name": "Admin"}
        )
        
        selector = TargetSelector('@target(type="User")')
        
        self.assertTrue(selector.matches(base_user))
        self.assertTrue(selector.matches(derived_user))
        self.assertFalse(selector.matches(other_user))

    def test_no_matches(self):
        """Test graceful handling when no entities match."""
        # Setup symbol table
        symbol_table = {
            "user1": EntityBlock(id="user1", class_name="User", location=self.location)
        }
        
        # Spec targeting "Admin" (none exist)
        spec = SpecBlock(
            name="test_admin",
            code='@target(type="Admin")\ndef test(subject): pass',
            location=self.location
        )
        
        documents = {
            MagicMock(path="test.td"): MagicMock(specs=[spec])
        }
        
        result = self.executor.execute_specs(documents, symbol_table, {})
        
        # Should pass (return True) because no tests failed (0 tests run)
        self.assertTrue(result)
        
        # Verify console log message about "no matching entities"
        # We need to check if the specific message was printed.
        # self.console.print.assert_any_call(...) involves rich text logic, 
        # so checking string containment in call args is easier.
        
        printed_msgs = [call.args[0] for call in self.console.print.call_args_list]
        found_msg = any("Spec 'None' has no matching entities" in str(msg) or "no matching entities" in str(msg) for msg in printed_msgs)
        self.assertTrue(found_msg, f"Expected 'no matching entities' message. Got: {printed_msgs}")

    def test_missing_target_decorator(self):
        """Test skipping specs without @target."""
        spec = SpecBlock(
            name="test_orphan",
            code='def test(subject): pass', # No decorator
            location=self.location,
            id="spec_orphan"
        )
        
        documents = {
            MagicMock(path="test.td"): MagicMock(specs=[spec])
        }
        
        result = self.executor.execute_specs(documents, {}, {})
        self.assertTrue(result)
        
        printed_msgs = [call.args[0] for call in self.console.print.call_args_list]
        found_msg = any("has no @target decorator" in str(msg) for msg in printed_msgs)
        self.assertTrue(found_msg)
