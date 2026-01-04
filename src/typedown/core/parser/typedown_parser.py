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
        # Strict Reference Pattern (L0 Hash | L1 System ID)
        # L0: sha256:...
        # L1: Alphanumeric, dots, dashes, underscores (no spaces)
        self.strict_ref_pattern = re.compile(r'^(?:sha256:[a-fA-F0-9]+|[a-zA-Z0-9_\.-]+)$')
        
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
        
        # Step 1: Traverse AST to build blocks (Entities, Models, etc.)
        self._traverse(ast, doc, path_str, navigator)

        # Step 2: Global Reference Scan (Based on full file content)
        doc.references = self._scan_all_references(content, path_str)
        
        # Step 3: Assign References to Blocks
        self._assign_references_to_blocks(doc)
        
        return doc
    
    def _scan_all_references(self, content: str, file_path: str) -> List[Reference]:
        refs = []
        for match in self.wiki_link_pattern.finditer(content):
            target = match.group(1)
            start_index = match.start()
            
            # Calculate absolute line number (1-indexed)
            line_no = content.count('\n', 0, start_index) + 1
            
            # Calculate column: Find last newline before start_index
            last_newline_idx = content.rfind('\n', 0, start_index)
            if last_newline_idx == -1:
                col_start = start_index 
            else:
                col_start = start_index - last_newline_idx - 1
            
            col_end = col_start + len(match.group(0))

            ref_loc = SourceLocation(
                file_path=file_path,
                line_start=line_no,
                line_end=line_no,
                col_start=col_start,
                col_end=col_end
            )
            
            refs.append(Reference(
                target=target,
                location=ref_loc
            ))
        return refs

    def _assign_references_to_blocks(self, doc: Document):
        """ assigns references to their containing blocks """
        for ref in doc.references:
            # Check Entities
            for ent in doc.entities:
                if ent.location and self._is_loc_contained(ref.location, ent.location):
                    # Strict validation for Entity Blocks: Only L0/L1 allowed
                    if self.strict_ref_pattern.match(ref.target):
                        ent.references.append(ref)
                    # Else: Ignore loose query refs inside Entity Blocks (treat as text)
            
            # Check Specs
            for spec in doc.specs:
                if spec.location and self._is_loc_contained(ref.location, spec.location):
                    spec.references.append(ref)
            
            # Check Models
            for model in doc.models:
                if model.location and self._is_loc_contained(ref.location, model.location):
                    # Models usually don't have references in syntax, but if they do:
                    pass

    def _is_loc_contained(self, inner: SourceLocation, outer: SourceLocation) -> bool:
        # Simple line containment
        return outer.line_start <= inner.line_start <= outer.line_end

    def _traverse(self, ast: List[Dict[str, Any]], doc: Document, file_path: str, navigator: 'LineNavigator'):
        for node in ast:
            node_type = node.get('type')
            
            if node_type == 'block_code':
                self._handle_code_block(node, doc, file_path, navigator)
            
            elif node_type == 'paragraph':
                text = self._get_text_content(node)
                # No need to scan references here, done globally
            
            elif node_type == 'heading':
                text = self._get_text_content(node)
                loc = navigator.find_text_block(text, file_path)
                doc.headers.append({
                    'title': text,
                    'level': node.get('level', 1),
                    'line': loc.line_start if loc else 0
                })
                # No need to scan references here, done globally
            
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

        # block_refs will be populated later by _assign_references
        block_refs = [] 

        if block_type == 'model':
            if block_arg:
                doc.models.append(ModelBlock(id=block_arg, code=code, location=loc))

        elif block_type == 'entity':
            if block_arg is None:
                header_parts = info_str.split()
                if len(header_parts) >= 2:
                    rest = " ".join(header_parts[1:])
                    if ':' in rest:
                        type_part, id_part = rest.split(':', 1)
                        type_name = type_part.strip()
                        entity_id = id_part.strip()
                        
                        if type_name and entity_id:
                            try:
                                data = yaml.safe_load(code)
                                if not isinstance(data, dict):
                                    data = {}
                                
                                # Enforce Signature as Identity
                                if 'id' in data:
                                    raise ValueError("Conflict: System ID must be defined in Block Signature, not in Body.")

                                doc.entities.append(EntityBlock(
                                    id=entity_id,
                                    class_name=type_name,
                                    raw_data=data,
                                    slug=None, # Deprecated: Body 'id' is no longer used as slug. Signature ID is the System ID.
                                    uuid=str(data.get('uuid')) if data.get('uuid') else None,
                                    former_ids=self._unbox_former(data.get('former')),
                                    derived_from_id=str(data.get('derived_from')) if data.get('derived_from') else None,
                                    location=loc,
                                    references=block_refs # To be filled
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
            spec_id = block_arg
            if spec_id:
                doc.specs.append(SpecBlock(
                    id=spec_id, 
                    name=spec_id, 
                    code=code, 
                    location=loc,
                    references=block_refs # To be filled
                ))

    def _unbox_former(self, raw_value: Any) -> List[str]:
        """
        Unbox former field which might be:
        - "slug" (Str)
        - ["slug"] (List[Str])
        - [["slug"]] (List[List[Str]] - Ref Sugar)
        """
        if not raw_value:
            return []
            
        if isinstance(raw_value, str):
            return [raw_value]
            
        if isinstance(raw_value, list):
            result = []
            for item in raw_value:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, list):
                    # Try to unbox ['slug']
                    if len(item) == 1 and isinstance(item[0], str):
                        result.append(item[0])
            return result
            
        return []

    def _scan_references(self, text: str, file_path: str, base_loc: Optional[SourceLocation] = None) -> List[Reference]:
        # Deprecated / Unused in favor of global scan
        return []

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
        start_search_idx = self.current_idx
        
        while True:
            for i in range(start_search_idx, len(self.lines)):
                line = self.lines[i]
                if line.strip().startswith("```") and info_str in line:
                    start_l = i + 1 # 1-indexed (header)
                    
                    # Try to find the exact column of info_str for better precision
                    col_start = line.find(info_str)
                    col_end = col_start + len(info_str)
                    
                    code_line_count = len(code.splitlines())
                    end_l = start_l + code_line_count + 1
                    
                    self.current_idx = end_l
                    return SourceLocation(
                        file_path=file_path,
                        line_start=start_l,
                        line_end=end_l,
                        col_start=col_start,
                        col_end=col_end
                    )
            
            # If not found and we started from middle, try from beginning once
            if start_search_idx > 0:
                start_search_idx = 0
            else:
                break
                
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
