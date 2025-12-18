import re
import hashlib
import frontmatter
import yaml
from pathlib import Path
from typing import List, Dict, Any, Tuple

from markdown_it import MarkdownIt
from typedown.core.ast import Document, EntityBlock, Reference, SourceLocation, EntityRef, SpecBlock

# Regex for matching [[query]]
# 匹配 [[query]] 但不匹配转义的 \[ \[query\]\]
REF_PATTERN = re.compile(r'(?<!\\)\[\[(.*?)\]\]')

class Parser:
    def __init__(self):
        self.md = MarkdownIt()

    def parse_file(self, file_path: Path, content_override: str = None) -> Document:
        """
        Parse a single Markdown file into a Document AST node.
        If content_override is provided, it is used instead of reading from disk.
        """
        try:
            if content_override is not None:
                content = content_override
            else:
                content = file_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")

        # 1. Calculate Hash
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # 2. Parse Front Matter
        # python-frontmatter handles YAML front matter between ---
        post = frontmatter.loads(content)
        metadata = post.metadata
        body = post.content

        # 3. Parse Markdown Tokens for Entities
        tokens = self.md.parse(body)
        
        entities: List[EntityBlock] = []
        specs: List[SpecBlock] = []
        python_scripts: List[str] = []
        model_scripts: List[str] = []
        
        # We need to track line offset because frontmatter removes lines
        # python-frontmatter doesn't tell us how many lines the FM took.
        # Simple heuristic: calculate lines of raw content - lines of body
        # FM lines = total - body - 1 (for the last newline usually)
        
        # Let's find where body starts in raw content
        body_start_line = 0
        if content.startswith("---"):
            # Simple manual scan for the second ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                fm_raw = parts[1]
                body_start_line = len(fm_raw.splitlines()) + 2 # +2 for the two ---

        for token in tokens:
            if token.type == "fence":
                info = token.info.strip()
                
                # Case 1: Python Code Block
                if info == "config:python":
                    python_scripts.append(token.content)

                # Case 1.5: Model Definition Block
                elif info == "model" or info.startswith("model:"):
                    # Inject auto-imports as per RFC 001
                    preamble = (
                        "from pydantic import BaseModel, Field, validator, model_validator, PrivateAttr\n"
                        "from typing import List, Dict, Optional, Union, Any, ClassVar\n"
                        "from enum import Enum\n"
                    )
                    full_script = preamble + token.content
                    model_scripts.append(full_script)
                
                # Case 2: Entity Block
                elif info.startswith("entity:"):
                    # Extract Class Name: "entity:User" -> "User"
                    class_name = info[len("entity:") :].strip()
                    
                    # Parse YAML content inside the block
                    try:
                        data = yaml.safe_load(token.content)
                        if not isinstance(data, dict):
                             # TODO: Log warning: Entity block must contain a dictionary
                             continue
                    except yaml.YAMLError:
                        # TODO: Log error: Invalid YAML in entity block
                        continue
                    
                    # Extract ID (Mandatory)
                    entity_id = data.get("id")
                    if not entity_id:
                        # TODO: Log error: Entity missing ID
                        continue

                    # Extract Relations
                    former_ref = None
                    if "former" in data:
                        former_ref = EntityRef(target_query=str(data.pop("former")))
                    
                    derived_from_ref = None
                    if "derived_from" in data:
                        derived_from_ref = EntityRef(target_query=str(data.pop("derived_from")))

                    # Calculate Source Location
                    # map is [start_line, end_line] in the body (0-indexed)
                    start_line = token.map[0] + body_start_line + 1 # +1 for 1-based indexing
                    end_line = token.map[1] + body_start_line
                    
                    loc = SourceLocation(
                        file_path=str(file_path),
                        line_start=start_line,
                        line_end=end_line
                    )

                    entities.append(EntityBlock(
                        id=entity_id,
                        class_name=class_name,
                        raw_data=data,
                        former_ref=former_ref,
                        derived_from_ref=derived_from_ref,
                        location=loc
                    ))

                # Case 2: Spec Block
                elif info.startswith("spec:") or info == "spec":
                    tag = info[len("spec:") :].strip() if ":" in info else "Rule"
                    
                    try:
                        data = yaml.safe_load(token.content)
                        if not isinstance(data, dict):
                            continue
                    except yaml.YAMLError:
                        continue
                        
                    spec_id = data.get("id")
                    if not spec_id:
                        continue
                    
                    # Mandatory fields for Spec
                    target = data.get("target")
                    check = data.get("check")
                    if not target or not check:
                        # TODO: Log error: Spec missing target or check
                        continue
                        
                    start_line = token.map[0] + body_start_line + 1 
                    end_line = token.map[1] + body_start_line
                    
                    loc = SourceLocation(
                        file_path=str(file_path),
                        line_start=start_line,
                        line_end=end_line
                    )
                    
                    specs.append(SpecBlock(
                        id=spec_id,
                        description=data.get("description"),
                        target=target,
                        check=check,
                        params=data.get("params", {}),
                        severity=data.get("severity", "warning"),
                        location=loc
                    ))

        # 4. Parse References using Regex
        # Note: This is a simple regex scan. Ideally, we should scan only text nodes in the AST
        # to avoid matching code blocks. But for MVP, global regex on body is acceptable.
        body_lines = body.splitlines()
        references: List[Reference] = []
        
        for line_idx, line in enumerate(body_lines):
            for match in REF_PATTERN.finditer(line):
                query = match.group(1)
                col_start = match.start() + 1 # +1 for 1-based
                col_end = match.end() + 1
                
                # Real line number
                real_line = line_idx + body_start_line + 1
                
                loc = SourceLocation(
                    file_path=str(file_path),
                    line_start=real_line,
                    line_end=real_line,
                    col_start=col_start,
                    col_end=col_end
                )
                
                references.append(Reference(
                    raw_text=match.group(0),
                    query_string=query,
                    location=loc
                ))

        return Document(
            path=file_path,
            content_hash=content_hash,
            config=metadata,
            entities=entities,
            specs=specs,
            references=references,
            python_scripts=python_scripts,
            model_scripts=model_scripts,
            raw_content=content
        )
