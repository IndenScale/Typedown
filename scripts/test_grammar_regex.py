import json
import re
import sys
from pathlib import Path

def test_grammar_regex():
    print("Testing Grammar Regex Logic...")
    
    # 1. Load Grammar
    grammar_path = Path("extensions/vscode/syntaxes/typedown.tmLanguage.json")
    if not grammar_path.exists():
        print(f"Error: {grammar_path} not found.")
        return
        
    try:
        with open(grammar_path, 'r') as f:
            grammar = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    # 2. Extract Regexes
    repo = grammar.get("repository", {})
    entity_block = repo.get("entity-block", {})
    reference_inline = repo.get("reference-inline", {})
    
    begin_regex_str = entity_block.get("begin")
    ref_regex_str = reference_inline.get("match")
    
    print(f"Entity Block Begin Regex: {begin_regex_str}")
    print(f"Reference Inline Regex: {ref_regex_str}")
    
    # 3. Compile Regexes (Python re is slightly different from Oniguruma, but good for basic validation)
    try:
        begin_pattern = re.compile(begin_regex_str)
        ref_pattern = re.compile(ref_regex_str)
    except re.error as e:
        print(f"Regex Compilation Error: {e}")
        return

    # 4. Test Cases
    
    # Case A: Entity Header
    header_line = "```entity Character: valen"
    match_header = begin_pattern.match(header_line)
    if match_header:
        print(f"\n[PASS] Header matched: '{header_line}'")
        print(f"  Groups: {match_header.groups()}")
    else:
        print(f"\n[FAIL] Header NOT matched: '{header_line}'")

    # Case B: Entity Header with Handles
    header_line_2 = "```entity Character: lyra"
    match_header_2 = begin_pattern.match(header_line_2)
    if match_header_2:
        print(f"\n[PASS] Header matched: '{header_line_2}'")
        print(f"  Groups: {match_header_2.groups()}")
    else:
        print(f"\n[FAIL] Header NOT matched: '{header_line_2}'")

    # Case C: Reference in List
    list_line = "  - [[item_potion_hp]]"
    match_ref = ref_pattern.search(list_line)
    if match_ref:
        print(f"\n[PASS] Reference found in list: '{list_line}'")
        print(f"  Match: '{match_ref.group(0)}'")
        print(f"  Groups: {match_ref.groups()}")
    else:
        print(f"\n[FAIL] Reference NOT found in list: '{list_line}'")

    # Case D: Reference alone
    ref_line = "[[item_sword]]"
    match_ref_2 = ref_pattern.search(ref_line)
    if match_ref_2:
        print(f"\n[PASS] Reference found alone: '{ref_line}'")
    else:
        print(f"\n[FAIL] Reference NOT found alone: '{ref_line}'")

if __name__ == "__main__":
    test_grammar_regex()
