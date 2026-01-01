
import logging
from pathlib import Path
from typing import Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

class TypedownEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[Path], Any], ignored_dirs=None):
        self.callback = callback
        self.ignored_dirs = ignored_dirs or [".git", "__pycache__", ".venv", "venv", "node_modules", ".gemini", ".idea", ".vscode"]

    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._process(event)

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        self._process(event)

    def on_deleted(self, event: FileSystemEvent):
        # Deleted files might need handle removal, but for now we treat as modified (will fail to read)
        if event.is_directory:
            return
        self._process(event)

    def _process(self, event: FileSystemEvent):
        path = Path(event.src_path)
        
        # Simple Extension Filter
        if path.suffix not in ['.td', '.md', '.markdown']:
            return

        # Ignore hidden/system dirs
        for part in path.parts:
            if part.startswith('.') and part != '.': # allow current dir
                return
            if part in self.ignored_dirs:
                return

        logging.info(f"FileWatcher detected change: {path}")
        self.callback(path)

class ProjectWatcher:
    """
    Wraps watchdog Observer to monitor project root.
    """
    def __init__(self, root_path: Path, callback: Callable[[Path], Any]):
        self.root_path = root_path
        self.callback = callback
        self.observer = Observer()
        self.handler = TypedownEventHandler(callback)

    def start(self):
        logging.info(f"Starting ProjectWatcher on {self.root_path}")
        self.observer.schedule(self.handler, str(self.root_path), recursive=True)
        self.observer.start()

    def stop(self):
        logging.info("Stopping ProjectWatcher...")
        self.observer.stop()
        self.observer.join()
