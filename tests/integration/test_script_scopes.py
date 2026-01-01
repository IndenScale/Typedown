
import os
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import MagicMock

# Assuming these imports work in the target environment
from typedown.core.compiler import Compiler
from typedown.core.base.config import TypedownConfig

class TestScriptScopes(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        # project_root/
        #   typedown.toml (Project Scope)
        #   subdir/
        #     config.td (Directory Scope)
        #     target.td (File Scope)
        
        self.test_dir = Path(tempfile.mkdtemp()).resolve()
        self.project_root = (self.test_dir / "project").resolve()
        self.project_root.mkdir()
        
        self.subdir = (self.project_root / "subdir").resolve()
        self.subdir.mkdir()
        
        # 1. Project Scope: typedown.toml
        self.config_file = self.project_root / "typedown.toml"
        self.config_file.write_text("""
[project]
name = "test_project"

[tasks]
project-task = "echo 'Running Project Task'"
overlap-task = "echo 'Project Overlap'"
""")

        # 2. Directory Scope: config.td
        self.dir_config = self.subdir / "config.td"
        self.dir_config.write_text("""---
scripts:
    dir-task: "echo 'Running Directory Task'"
    overlap-task: "echo 'Directory Overlap'"
---
""")

        # 3. File Scope: target.td
        self.target_file = self.subdir / "target.td"
        self.target_file.write_text("""---
scripts:
    file-task: "echo 'Running File Task'"
    overlap-task: "echo 'File Overlap'"
---
entity User: alice
""")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_run_script_project_scope(self):
        """Test simple project scope task execution"""
        compiler = Compiler(self.project_root, console=MagicMock())
        
        # Mock ScriptRunner execution to verify logic without actual shell calls
        with unittest.mock.patch('typedown.core.compiler.ScriptRunner') as MockRunner:
            instance = MockRunner.return_value
            instance.run_script.return_value = 0
            
            result = compiler.run_script("project-task", target_file=self.target_file)
            
            # Verify compiler found it and passed to runner
            self.assertEqual(result, 0)
            instance.run_script.assert_called_with(
                "project-task", 
                target_file=self.target_file,
                file_scripts={"file-task": "echo 'Running File Task'", "overlap-task": "echo 'File Overlap'"}, # File scripts are loaded from target doc
                dir_scripts={"dir-task": "echo 'Running Directory Task'", "overlap-task": "echo 'Directory Overlap'"},
                project_scripts={'project-task': "echo 'Running Project Task'", 'overlap-task': "echo 'Project Overlap'"},
                dry_run=False
            )

    def test_run_script_directory_scope(self):
        """Test directory scope task discovery"""
        compiler = Compiler(self.project_root, console=MagicMock())
        
        with unittest.mock.patch('typedown.core.compiler.ScriptRunner') as MockRunner:
            instance = MockRunner.return_value
            instance.run_script.return_value = 0
            
            result = compiler.run_script("dir-task", target_file=self.target_file)
            
            self.assertEqual(result, 0)
            call_args = instance.run_script.call_args[1]
            self.assertIn("dir-task", call_args['dir_scripts'])

    def test_scoping_precedence(self):
        """
        Verify that Compiler passes all scopes to ScriptRunner.
        Compiler does NOT resolve precedence; ScriptRunner does.
        We just check that all dicts are correctly populated.
        """
        compiler = Compiler(self.project_root, console=MagicMock())
        
        with unittest.mock.patch('typedown.core.compiler.ScriptRunner') as MockRunner:
            instance = MockRunner.return_value
            instance.run_script.return_value = 0
            
            compiler.run_script("overlap-task", target_file=self.target_file)
            
            args = instance.run_script.call_args[1]
            # Verify all layers have the 'overlap-task'
            self.assertEqual(args['file_scripts']['overlap-task'], "echo 'File Overlap'")
            self.assertEqual(args['dir_scripts']['overlap-task'], "echo 'Directory Overlap'")
            self.assertEqual(args['project_scripts']['overlap-task'], "echo 'Project Overlap'")

if __name__ == '__main__':
    unittest.main()
