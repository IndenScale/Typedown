"""Completion service - LSP protocol independent completion logic."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import re

from lsprotocol.types import CompletionItem, CompletionItemKind, CompletionList

from typedown.core.compiler import Compiler


@dataclass
class CompletionContext:
    """Context for completion request, independent of LSP protocol."""
    file_path: Path
    content: str
    line: int  # 0-indexed
    character: int  # 0-indexed


class CompletionService:
    """
    Service layer for completion logic.
    
    This class provides LSP protocol-independent completion functionality,
    allowing both LSP server and CLI to share the same completion logic.
    """
    
    def __init__(self, compiler: Compiler):
        self.compiler = compiler
    
    def complete(self, context: CompletionContext) -> Union[CompletionList, List[CompletionItem]]:
        """
        Get completions for a given context.
        
        Args:
            context: The completion context including file, content, and position.
            
        Returns:
            A CompletionList or list of CompletionItems.
        """
        lines = context.content.splitlines()
        if context.line >= len(lines):
            return []
        
        line = lines[context.line]
        col = context.character
        prefix = line[:col]
        
        items = []
        
        # CASE 1: [[class:
        class_match = re.search(r'\[\[class:([\w\.\-_]*)$', prefix)
        if class_match:
            return self._complete_class_scope()
        
        # CASE 2: [[entity:
        entity_match = re.search(r'\[\[entity:([\w\.\-_]*)$', prefix)
        if entity_match:
            return self._complete_entity_scope()
        
        # CASE 3: [[header:
        header_match = re.search(r'\[\[header:([\w\.\-_ ]*)$', prefix)
        if header_match:
            return self._complete_header_scope()
        
        # CASE 4: Generic [[
        match = re.search(r'\[\[([^:\]]*)$', prefix)
        if match:
            return self._complete_generic()
        
        return []
    
    def _complete_class_scope(self) -> CompletionList:
        """Complete for [[class: scope - show all known Models."""
        items = []
        if hasattr(self.compiler, 'model_registry'):
            for model_name, model_cls in self.compiler.model_registry.items():
                items.append(CompletionItem(
                    label=model_name,
                    kind=CompletionItemKind.Class,
                    detail="Model",
                    documentation=model_cls.__doc__ or f"Pydantic Model {model_name}",
                    insert_text=f"{model_name}]]",
                    sort_text=f"00_{model_name}"
                ))
        return CompletionList(is_incomplete=False, items=items)
    
    def _complete_entity_scope(self) -> CompletionList:
        """Complete for [[entity: scope - show all known Entities."""
        items = []
        for key, entity in self.compiler.symbol_table.items():
            # Determine System ID (L1) vs Handle (L2)
            system_id = getattr(entity, 'id', key)
            
            # Check if it's a HandleWrapper pointing to an Entity
            if hasattr(entity, 'value') and hasattr(entity.value, 'id'):
                system_id = entity.value.id
                detail_text = f"Handle -> {system_id}"
            else:
                detail_text = getattr(entity, 'class_name', "Entity")
            
            items.append(CompletionItem(
                label=key,
                kind=CompletionItemKind.Class,
                detail=detail_text,
                documentation=f"Defined in {getattr(getattr(entity, 'location', None), 'file_path', 'Unknown')}",
                insert_text=f"{system_id}]]",
                sort_text=f"00_{key}"
            ))
        return CompletionList(is_incomplete=False, items=items)
    
    def _complete_header_scope(self) -> CompletionList:
        """Complete for [[header: scope - show all known Headers from all docs."""
        items = []
        for doc_path, doc in self.compiler.documents.items():
            for hdr in doc.headers:
                title = hdr.get('title', 'Untitled')
                level = hdr.get('level', 1)
                items.append(CompletionItem(
                    label=title,
                    kind=CompletionItemKind.Reference,
                    detail=f"H{level} in {doc_path.name}",
                    insert_text=f"{title}]]",
                    sort_text=f"00_{title}"
                ))
        return CompletionList(is_incomplete=False, items=items)
    
    def _complete_generic(self) -> CompletionList:
        """Complete for generic [[ - snippets, entities, and files."""
        items = []
        
        # 1. Snippets
        for snip in ["entity:", "class:", "header:"]:
            items.append(CompletionItem(
                label=snip,
                kind=CompletionItemKind.Keyword,
                detail=f"Scope to {snip[:-1]}",
                insert_text=snip,
                sort_text=f"00_{snip}_snippet",
                command={'title': 'Trigger Completion', 'command': 'editor.action.triggerSuggest'}
            ))
        
        # 2. Entities (Icon: Class/Struct)
        for key, entity in self.compiler.symbol_table.items():
            # Determine System ID (L1) vs Handle (L2)
            system_id = getattr(entity, 'id', key)
            
            # Check if it's a HandleWrapper pointing to an Entity
            if hasattr(entity, 'value') and hasattr(entity.value, 'id'):
                system_id = entity.value.id
                detail_text = f"Handle -> {system_id}"
            else:
                detail_text = getattr(entity, 'class_name', "Entity")
            
            items.append(CompletionItem(
                label=key,
                kind=CompletionItemKind.Struct,
                detail=detail_text,
                documentation=f"Defined in {getattr(getattr(entity, 'location', None), 'file_path', 'Unknown')}",
                insert_text=f"{system_id}]]",
                sort_text=f"10_{key}"
            ))
        
        # 3. Files (Icon: File)
        for doc_path in self.compiler.documents.keys():
            path_name = doc_path.name
            items.append(CompletionItem(
                label=path_name,
                kind=CompletionItemKind.File,
                detail="File",
                insert_text=f"{path_name}]]",
                sort_text=f"20_{path_name}"
            ))
        
        return CompletionList(is_incomplete=False, items=items)
