import os
import shutil
import sys
import yaml
from pathlib import Path

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def sync_path(source_root, dest_root, item, source_base, dest_base):
    """
    Syncs a single item (file or directory) from source to destination.
    source_root: Absolute path to the source root (e.g., .../Typedown/docs)
    dest_root: Absolute path to the destination root (e.g., .../Typedown/website/public/docs)
    item: Relative path item to sync (e.g., "zh")
    """
    src_item_path = source_root / item
    dest_item_path = dest_root / item

    if not src_item_path.exists():
        print(f"[WARN] Source path does not exist: {src_item_path}")
        return

    print(f"[SYNC] {item} -> {dest_item_path}")

    if src_item_path.is_dir():
        if dest_item_path.exists():
            shutil.rmtree(dest_item_path)
        shutil.copytree(src_item_path, dest_item_path, dirs_exist_ok=True)
    else:
        # It's a file
        dest_item_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_item_path, dest_item_path)

def main():
    root_dir = Path(__file__).resolve().parent.parent
    config_path = root_dir / "website" / "content_sync.yaml"

    if not config_path.exists():
        print(f"[ERROR] Config file not found: {config_path}")
        sys.exit(1)

    config = load_config(config_path)
    
    # We execute from the project root perspective usually, but let's be absolute
    
    for target in config.get('sync_targets', []):
        source_dir = root_dir / target['source']
        dest_dir = root_dir / target['destination']
        
        print(f"\nProcessing Target: {target['source']} -> {target['destination']}")

        # Ensure destination exists or at least parent
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
            
        # Clean destination if requested?
        # The prompt implies we want to control what's public.
        # If we just copy 'include' items, we might leave stale items if we don't clean first.
        # But 'destination' might be 'website/public/docs'. Wiping it is generally safe if we re-sync everything.
        
        # However, to be safe and support partial updates, let's just process the 'include' list.
        # BUT, if we rename a file in source, the old one remains in dest.
        # Given "clean_destination: true", let's wipe the destination directory specifically for the included items?
        # No, the simplest robust way for "Consistency" is:
        # 1. content_sync says: "Sync `docs/zh` to `website/public/docs/zh`"
        # If we want exact mirror of the allowed subset:
        # We should probably clear `website/public/docs` if we are syncing the whole structure.
        
        # Let's trust the "include" list.
        # If "clean_destination" is true, we might want to empty the destination root first.
        # BUT `website/public/docs` is just for docs.
        
        if config.get('options', {}).get('clean_destination', False):
             if dest_dir.exists():
                 print(f"[CLEAN] Removing {dest_dir}")
                 shutil.rmtree(dest_dir)
                 dest_dir.mkdir(parents=True, exist_ok=True)

        for item in target.get('include', []):
            sync_path(source_dir, dest_dir, item, source_dir, dest_dir)

if __name__ == "__main__":
    main()
