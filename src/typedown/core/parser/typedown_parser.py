import mistune
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from mistune.plugins.def_list import def_list
from typedown.core.ast import (
    Document, EntityBlock, ModelBlock, SpecBlock, Reference, SourceLocation, ConfigBlock
)
from .utils import InfoStringParser

class TypedownParser:
    def __init__(self):
        # renderer=None tells mistune to return AST when calling parse()
        self.mistune = mistune.create_markdown(
            renderer=None,
            plugins=[def_list]
        )
        # Wiki link pattern: [[Target]]
        self.wiki_link_pattern = re.compile(r'\[\[(.*?)\]\]')
        # Front Matter pattern: ---\n...\n---
        self.front_matter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

    def parse(self, file_path: Path) -> Document:
        try:
            content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        return self.parse_text(content, str(file_path))

    def parse_text(self, content: str, path_str: str) -> Document:
        # Extract Front Matter if present
        front_matter_data = {}
        markdown_content = content
        
        match = self.front_matter_pattern.match(content)
        if match:
            front_matter_str = match.group(1)
            try:
                front_matter_data = yaml.safe_load(front_matter_str) or {}
            except yaml.YAMLError:
                pass
            else:
                markdown_content = content[match.end():]
        
        # Mistune v3: parse() returns (ast, state)
        ast, state = self.mistune.parse(markdown_content)
        
        doc = Document(
            path=Path(path_str), 
            raw_content=content,
            tags=front_matter_data.get('tags', []),
            scripts=front_matter_data.get('scripts', {})
        )
        
        # Initialize Line Navigator for accurate position tracking
        navigator = LineNavigator(content)
        self._traverse(ast, doc, path_str, navigator)
        
        return doc

    def _traverse(self, ast: List[Dict[str, Any]], doc: Document, file_path: str, navigator: 'LineNavigator'):
        for node in ast:
            node_type = node.get('type')
            
            if node_type == 'block_code':
                self._handle_code_block(node, doc, file_path, navigator)
            
            elif node_type == 'paragraph':
                text = self._get_text_content(node)
                loc = navigator.find_text_block(text, file_path)
                refs = self._scan_references(text, file_path, loc)
                doc.references.extend(refs)

            elif node_type == 'heading':
                text = self._get_text_content(node)
                loc = navigator.find_text_block(text, file_path)
                doc.headers.append({
                    'title': text,
                    'level': node.get('level', 1),
                    'line': loc.line_start if loc else 0
                })
                refs = self._scan_references(text, file_path, loc)
                doc.references.extend(refs)
            
            # Recursive traversal
            if 'children' in node:
                self._traverse(node['children'], doc, file_path, navigator)

    def _handle_code_block(self, node: Dict[str, Any], doc: Document, file_path: str, navigator: 'LineNavigator'):
        attrs = node.get('attrs', {})
        info_str = attrs.get('info', '') if attrs else (node.get('info', '') or '')
        code = node.get('text', '') or node.get('raw', '')
        
        # Parse info string
        parts = info_str.split()
        if not parts:
            return

        block_type, block_arg, meta = InfoStringParser.parse(info_str)
        
        # Accurate Location Tracking
        loc = navigator.find_code_block(info_str, code, file_path)

        # Pre-scan references in this block
        block_refs = self._scan_references(code, file_path, loc)
        doc.references.extend(block_refs)

        if block_type == 'model':
            if block_arg:
                doc.models.append(ModelBlock(id=block_arg, code=code, location=loc))

        elif block_type == 'entity':
            type_name = None
            entity_id = None
            
            # Use improved entity parsing logic
            if block_arg and len(parts) >= 2:
                # entity:Type ID
                type_name = block_arg
                entity_id = parts[1]
            elif len(parts) >= 2 and parts[0] == 'entity':
                # entity Type: ID or entity Type:ID
                rest = " ".join(parts[1:])
                if ':' in rest:
                    type_part, id_part = rest.split(':', 1)
                    type_name = type_part.strip()
                    entity_id = id_part.strip()

            if type_name and entity_id:
                try:
                    data = yaml.safe_load(code)
                    if not isinstance(data, dict):
                        data = {}
                    
                    doc.entities.append(EntityBlock(
                        id=entity_id,
                        class_name=type_name,
                        raw_data=data,
                        slug=str(data.get('id')) if data.get('id') else None,
                        uuid=str(data.get('uuid')) if data.get('uuid') else None,
                        former_ids=[data.get('former')] if isinstance(data.get('former'), str) else (data.get('former') or []),
                        derived_from_id=str(data.get('derived_from')) if data.get('derived_from') else None,
                        location=loc,
                        references=block_refs
                    ))
                except yaml.YAMLError:
                    pass

        elif block_type == 'config':
            if block_arg == 'python':
                 meta = InfoStringParser.parse(info_str)[2]
                 config_id = meta.get('id')
                 doc.configs.append(ConfigBlock(
                     id=config_id,
                     code=code,
                     location=loc
                 ))

        elif block_type == 'spec':
            spec_id = block_arg or meta.get('id')
            if not spec_id:
                spec_id = f"spec_{len(doc.specs) + 1}"
            
            doc.specs.append(SpecBlock(
                id=spec_id, 
                name=spec_id, 
                code=code, 
                target=meta.get('target'),
                location=loc,
                references=block_refs
            ))

    def _scan_references(self, text: str, file_path: str, base_loc: Optional[SourceLocation] = None) -> List[Reference]:
        refs = []
        for match in self.wiki_link_pattern.finditer(text):
            target = match.group(1)
            line_offset = text[:match.start()].count('\n')
            
            ref_loc = SourceLocation(
                file_path=file_path,
                line_start=(base_loc.line_start + line_offset) if base_loc else 0,
                line_end=(base_loc.line_start + line_offset) if base_loc else 0
            )
            
            refs.append(Reference(
                target=target,
                location=ref_loc
            ))
        return refs

    def _get_text_content(self, node: Dict[str, Any]) -> str:
        text = ""
        if 'text' in node:
            text += node['text']
        elif 'raw' in node:
            text += node['raw']
            
        if 'children' in node:
            for child in node['children']:
                text += self._get_text_content(child)
        return text

class LineNavigator:
    """Helper to track line numbers in the original source content."""
    def __init__(self, content: str):
        self.lines = content.splitlines()
        self.current_idx = 0 # 0-indexed line pointer

    def find_code_block(self, info_str: str, code: str, file_path: str) -> SourceLocation:
        # Search for header line
        for i in range(self.current_idx, len(self.lines)):
            line = self.lines[i].strip()
            if line.startswith("```") and info_str in line:
                start_l = i + 1 # 1-indexed (header)
                
                # Splitlines handles training newlines by not creating a blank final list item
                # but code blocks might have meaningful trailing newlines.
                # However, Markdown physical lines are what counts.
                code_line_count = len(code.splitlines())
                
                # Header (1) + Code (n) + Footer (1)
                end_l = start_l + code_line_count + 1
                
                # Update navigator index to after the footer
                self.current_idx = end_l
                return SourceLocation(
                    file_path=file_path,
                    line_start=start_l,
                    line_end=end_l
                )
        return SourceLocation(file_path=file_path, line_start=0, line_end=0)

    def find_text_block(self, text: str, file_path: str) -> SourceLocation:
        if not text: 
            return SourceLocation(file_path=file_path, line_start=0, line_end=0)
        
        # Heading or Paragraph
        search_text = text.splitlines()[0].strip()
        for i in range(self.current_idx, len(self.lines)):
            if search_text in self.lines[i]:
                line_n = i + 1
                self.current_idx = i
                return SourceLocation(
                    file_path=file_path,
                    line_start=line_n,
                    line_end=line_n + len(text.splitlines()) - 1
                )
        return SourceLocation(file_path=file_path, line_start=0, line_end=0)
