
import os
import re
import argparse
from pathlib import Path

# Regex to match the start of an entity block
# Captures: 1=indent, 2=entity type, 3=signature id
ENTITY_START_RE = re.compile(r'^(\s*)```entity\s+([\w\.]+):\s*([\w\.\-_]+)\s*$')
ENTITY_END_RE = re.compile(r'^\s*```\s*$')
# Regex to match id field in YAML body (assumes simple key-value)
ID_FIELD_RE = re.compile(r'^(\s*)id:\s*(["\']?)([\w\.\-_]+)\2\s*$')

def process_file(file_path: Path, dry_run: bool = False):
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        print(f"Skipping binary or non-utf8 file: {file_path}")
        return

    lines = content.splitlines()
    new_lines = []
    modified = False
    in_entity_block = False
    current_signature_id = None
    block_indent = ""

    for i, line in enumerate(lines):
        # Check for block start
        start_match = ENTITY_START_RE.match(line)
        if start_match:
            in_entity_block = True
            block_indent = start_match.group(1)
            current_signature_id = start_match.group(3)
            new_lines.append(line)
            continue

        # Check for block end
        if in_entity_block and ENTITY_END_RE.match(line):
            in_entity_block = False
            current_signature_id = None
            new_lines.append(line)
            continue

        # Process lines inside entity block
        if in_entity_block:
            id_match = ID_FIELD_RE.match(line)
            if id_match:
                # Found an id field
                body_id = id_match.group(3)
                
                # Verify match (Optional, just logging)
                if body_id != current_signature_id:
                    print(f"WARNING: ID Mismatch in {file_path}:{i+1}")
                    print(f"  Signature: {current_signature_id}")
                    print(f"  Body:      {body_id}")
                    print(f"  Action:    Removing body ID (Signature is authoritative)")
                else:
                    print(f"INFO: Removing redundant ID '{body_id}' in {file_path}:{i+1}")

                modified = True
                continue # Skip adding this line to new_lines
        
        new_lines.append(line)

    if modified:
        if not dry_run:
            # Reconstruct content. Note: splitlines consumes line endings, so we assume \n
            new_content = "\n".join(new_lines) + "\n" 
            # Check if original had trailing newline behavior to preserve perfectly? 
            # splitlines() drops the last \n if content ends with it. 
            # A simple join("\n") is usually safe for text files.
            file_path.write_text(new_content, encoding='utf-8')
            print(f"UPDATED: {file_path}")
        else:
            print(f"WOULD UPDATE: {file_path}")

def main():
    parser = argparse.ArgumentParser(description="Cleanup 'id' fields from entity block bodies.")
    parser.add_argument("root_dir", type=str, nargs="?", default=".", help="Root directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without modifying files")
    args = parser.parse_args()

    root = Path(args.root_dir).resolve()
    print(f"Scanning {root}...")

    # Exclusion list
    excludes = {'.git', '.venv', 'venv', 'node_modules', '__pycache__', '.pytest_cache', 'dist', 'build'}

    for current_dir, dirs, files in os.walk(root):
        # Modify dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in excludes]

        for file in files:
            if file.endswith(('.td', '.md', '.markdown')):
                file_path = Path(current_dir) / file
                process_file(file_path, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
