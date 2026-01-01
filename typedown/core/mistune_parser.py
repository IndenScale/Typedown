import mistune
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List
from mistune.plugins.def_list import def_list

from typedown.core.ir import (
    Document, EntityDef, ModelDef, SpecDef, Reference, SourceLocation, ConfigDef
)

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

    def parse_text(self, content: str, fake_path: str = "<memory>") -> Document:
        """Parse raw string content directly."""
        # Mistune v3: parse() returns (ast, state)
        ast, state = self.markdown.parse(content)
        
        doc = Document(path=Path(fake_path), raw_content=content)
        
        self._traverse(ast, doc, fake_path)
        
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

            elif node_type == 'heading':
                text_content = self._get_text_content(node)
                # Capture header
                doc.headers.append({
                    'title': text_content,
                    'level': node.get('level', 1),
                    'line': 0 # TODO: Accurate location from AST if available
                })
                # Check for refs in header too
                self._scan_references(text_content, doc, file_path)
            
            # Recursive traversal for nested structures (lists, blockquotes)
            if 'children' in node:
                self._traverse(node['children'], doc, file_path)

    def _handle_code_block(self, node: Dict[str, Any], doc: Document, file_path: str):
        # Mistune v3 stores info string in attrs['info']
        attrs = node.get('attrs', {})
        info_str = attrs.get('info', '') if attrs else ''
        
        if not info_str:
             info_str = node.get('info', '') or ''
        
        code = node.get('text', '') or node.get('raw', '')
        
        # Parse info string: "entity ClassName: EntityID"
        parts = info_str.split()
        if not parts:
            return
            
        block_type = parts[0]
        
        # Enforce strict syntax: ```entity ClassName: EntityID```
        if block_type == 'entity':
            if len(parts) < 3:
                # Invalid syntax, ignore or log
                return
            
            raw_type = parts[1]
            if not raw_type.endswith(':'):
                 # Strict syntax requires colon? User said "ClassName: EntityID"
                 # We'll allow missing colon if it's unambiguous, but let's prefer stripping it.
                 # Actually user said "Unique reasonable syntax is ent CLs: ID". Let's enforce colon?
                 # Flexible reading: strip colon if present.
                 pass
            
            type_name = raw_type.rstrip(':')
            entity_id = parts[2]
            
            # Additional metadata might follow? User didn't specify. 
            # Assuming strictly ID is the last mandatory part.
            
            # Reconstruct location
            loc = SourceLocation(file_path=file_path, line_start=0, line_end=0) 

            try:
                data = yaml.safe_load(code)
                if isinstance(data, dict):
                    # Inject ID into data
                    data['id'] = entity_id
                    
                    doc.entities.append(EntityDef(
                        id=entity_id,
                        type_name=type_name,
                        data=data,
                        location=loc
                    ))
            except yaml.YAMLError:
                pass

        elif block_type == "model":
            # Models might use "model ClassName" or just "model" with code defining it.
            # Keeping existing permissive model logic for now unless instructed otherwise.
            loc = SourceLocation(file_path=file_path, line_start=0, line_end=0)
            meta = {}
            for p in parts[1:]:
                 if '=' in p:
                     k,v = p.split('=', 1)
                     meta[k] = v.strip('"\'')
            node_id = meta.get('id')
            doc.models.append(ModelDef(id=node_id, code=code, location=loc)) 

        elif block_type == "spec":
            # Spec Block (Python/Pytest)
            # Parse meta for ID
            meta = {}
            for p in parts[1:]:
                 if '=' in p:
                     k,v = p.split('=', 1)
                     meta[k] = v.strip('"\'')
            node_id = meta.get('id')
            
            doc.specs.append(SpecDef(id=node_id, name=node_id or "spec_block", code=code, location=loc))
        
        elif block_type.startswith("spec:"):
            # YAML Spec
            meta = {}
            for p in parts[1:]:
                 if '=' in p:
                     k,v = p.split('=', 1)
                     meta[k] = v.strip('"\'')
            node_id = meta.get('id')

            try:
                data = yaml.safe_load(code)
                if isinstance(data, dict):
                    spec_id = node_id or data.get("id")
                    if spec_id:
                        doc.specs.append(SpecDef(id=spec_id, name=spec_id, code=code, data=data, location=loc))
            except yaml.YAMLError:
                pass

        elif block_type.startswith("config:python"):
            meta = {}
            for p in parts[1:]:
                 if '=' in p:
                     k,v = p.split('=', 1)
                     meta[k] = v.strip('"\'')
            node_id = meta.get('id')

            doc.configs.append(ConfigDef(
                id=node_id,
                code=code,
                location=loc
            ))
        
        # Scan for inline references [[...]] in all code blocks
        self._scan_references(code, doc, file_path)

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
