import mistune
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List
from mistune.plugins.def_list import def_list

from typedown.core.ir import (
    Document, EntityDef, ModelDef, SpecDef, ImportStmt, Reference, SourceLocation
)

# Regex for finding imports in python code (simple heuristic)
IMPORT_REGEX = re.compile(r"^\s*from\s+([@\w\.]+)\s+import\s+(.+)$", re.MULTILINE)

class TypedownParser:
    def __init__(self):
        # renderer=None tells mistune to return AST when calling parse()
        self.markdown = mistune.create_markdown(
            renderer=None,
            plugins=[def_list]
        )
        # Wiki link pattern: [[Target]]
        self.wiki_link_pattern = re.compile(r'\[\[(.*?)\]\]')

    def parse(self, file_path: Path) -> Document:
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        # Mistune v3: parse() returns (ast, state)
        ast, state = self.markdown.parse(content)
        
        doc = Document(path=file_path, raw_content=content)
        
        # Traverse Mistune AST and convert to Typedown IR
        self._traverse(ast, doc, str(file_path))
        
        return doc

    def _traverse(self, ast: List[Dict[str, Any]], doc: Document, file_path: str):
        # We need to track line numbers. Mistune AST often provides 'loc' tuples (start_line, end_line)
        # But AstRenderer might not populate it by default unless enabled?
        # Actually Mistune's block parser populates 'loc' if enabled.
        # Let's assume we can get basic info or infer it.
        # For now, simplistic traversal.

        for node in ast:
            node_type = node.get('type')
            
            if node_type == 'block_code':
                self._handle_code_block(node, doc, file_path)
            
            elif node_type == 'paragraph':
                # Scan for inline references [[...]]
                text_content = self._get_text_content(node)
                self._scan_references(text_content, doc, file_path)
            
            # Recursive traversal for nested structures (lists, blockquotes)
            if 'children' in node:
                self._traverse(node['children'], doc, file_path)

    def _handle_code_block(self, node: Dict[str, Any], doc: Document, file_path: str):
        # Mistune v3 stores info string in attrs['info']
        attrs = node.get('attrs', {})
        info = attrs.get('info', '') if attrs else ''
        
        # Fallback for old structure just in case or if no attrs
        if not info:
             info = node.get('info', '') or ''
        
        code = node.get('text', '') or node.get('raw', '') # Mistune v3 uses 'raw' for code content often
        
        # Determine location (Mistune might not strictly provide line numbers in basic AST)
        # TODO: Enhance Mistune configuration to ensure 'loc' is present.
        loc = SourceLocation(file_path=file_path, line_start=0, line_end=0) 

        if info.startswith("entity:"):
            # Entity Block
            type_name = info[len("entity:") :].strip()
            try:
                data = yaml.safe_load(code)
                if isinstance(data, dict):
                    entity_id = data.get("id")
                    if entity_id:
                        doc.entities.append(EntityDef(
                            id=entity_id,
                            type_name=type_name,
                            data=data,
                            location=loc
                        ))
            except yaml.YAMLError:
                pass # Log error

        elif info.startswith("model"):
            # Model Block
            doc.models.append(ModelDef(code=code, location=loc))

        elif info.startswith("spec"):
            # Spec Block
            doc.specs.append(SpecDef(name="spec_block", code=code, location=loc))

        elif info == "config:python":
            # Config Block - Extract imports
            # We are manually parsing python imports here to feed the 'ImportStmt'
            # This is the key for the Resolver to work!
            for match in IMPORT_REGEX.finditer(code):
                source = match.group(1) # e.g., @lib.math
                names_str = match.group(2) # e.g., MathConfig, Other
                names = [n.strip() for n in names_str.split(',')]
                
                doc.imports.append(ImportStmt(
                    source=source,
                    names=names,
                    location=loc
                ))

    def _scan_references(self, text: str, doc: Document, file_path: str):
        for match in self.wiki_link_pattern.finditer(text):
            target = match.group(1)
            doc.references.append(Reference(
                target=target,
                location=SourceLocation(file_path=file_path, line_start=0, line_end=0)
            ))

    def _get_text_content(self, node: Dict[str, Any]) -> str:
        """Helper to extract raw text from a node's children"""
        text = ""
        if 'text' in node:
            text += node['text']
        if 'children' in node:
            for child in node['children']:
                text += self._get_text_content(child)
        return text
