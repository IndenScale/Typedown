import sys
import os
import asyncio
import json
import logging
from types import ModuleType

# Set CWD to root so we can find the files written to /world etc.
os.chdir("/")
# print(f"DEBUG: CWD changed to: {os.getcwd()}")

# --- HACK START: Mock watchdog ---
m_watchdog = ModuleType("watchdog")
sys.modules["watchdog"] = m_watchdog
m_events = ModuleType("watchdog.events")
sys.modules["watchdog.events"] = m_events
m_observers = ModuleType("watchdog.observers")
class MockObserver:
    def schedule(self, *args, **kwargs): pass
    def start(self): pass
    def stop(self): pass
    def join(self): pass
    def unschedule_all(self): pass
m_observers.Observer = MockObserver
sys.modules["watchdog.observers"] = m_observers
class FileSystemEventHandler: pass
class FileSystemEvent: pass
m_events.FileSystemEventHandler = FileSystemEventHandler
m_events.FileSystemEvent = FileSystemEvent
# --- HACK END ---

# Import Server
from typedown.server.application import server
import pygls
from pygls.protocol import LanguageServerProtocol
from lsprotocol.types import TextDocumentSyncKind

# Use Full Sync for simplicity with OverlayProvider (Memory Overlay).
# Compiler replaces the entire file content in memory.
server.text_document_sync_kind = TextDocumentSyncKind.Full

# Check version robustly
try:
    from importlib.metadata import version
    ver = version("pygls")
    # print(f"DEBUG: Python Kernel 3, pygls version: {ver}")
except:
    # print("DEBUG: Python Kernel 3, pygls version: unknown")
    pass

# Redirect stdout/stderr with filtering
class JSWriter:
    def __init__(self, name="STDOUT"):
        self.name = name

    def write(self, message):
        import js
        msg = message.strip()
        if not msg:
            return
            
        # Filter out noisy DEBUG messages unless explicitly requested
        if msg.startswith("DEBUG:") or msg.startswith("INFO:pygls"):
            return
        
        # Filter out LSP protocol noise
        if "Sending data" in msg or "publishDiagnostics" in msg:
            return
        
        # Filter out WARNING messages for unknown methods (expected in Playground)
        if msg.startswith("WARNING:"):
            return
            
        # Special handling for repetitive LSP notifications
        if "semantic_tokens" in msg or "didChangeConfiguration" in msg:
            return

        js.console.log(f"[{self.name}] {msg}")

    def flush(self): pass

sys.stdout = JSWriter("Kernel")
sys.stderr = JSWriter("Error")

# Configure logging to use our JSWriter
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("typedown")
logger.setLevel(logging.INFO)

# =========================================================
#  LSP Transport for WASM (asyncio)
# =========================================================
class WebTransport(asyncio.Transport):
    def __init__(self):
        self._closed = False
        self._extra = {}

    def close(self):
        self._closed = True

    def is_closing(self):
        return self._closed
    
    def get_extra_info(self, name, default=None):
        return self._extra.get(name, default)

    def write(self, data):
        if self._closed: return
        try:
            msg_str = data if isinstance(data, str) else data.decode('utf-8')
            parts = msg_str.split('\r\n\r\n', 1)
            
            body = ""
            if len(parts) == 2:
                body = parts[1]
            elif msg_str.strip().startswith('{'):
                body = msg_str
            else:
                 print(f"DEBUG: Transport got non-JSON format: {msg_str[:50]}...")
                 return

            if body:
                import js
                js.post_lsp_message(body)

        except Exception as e:
            # Use logging instead of print for transport errors
            logging.error(f"Transport Write Error: {e}")

# =========================================================
#  Wiring
# =========================================================

transport = WebTransport()

def wire_server():
    # 1. Ensure Protocol is Initialized
    if server.protocol is None:
        # print("DEBUG: server.protocol is None. Manually initializing LanguageServerProtocol...")
        server.protocol = LanguageServerProtocol(server)
    
    protocol = server.protocol
    
    # 2. Connect Output (Python -> JS)
    # First Principles: pygls v2 separates Protocol (Logic) from IO (Transport).
    # We must provide a 'writer' object.
    
    success = False
    
    # Preferred: set_writer (v2 standard)
    if hasattr(protocol, 'set_writer'):
        try:
            protocol.set_writer(transport)
            # print("DEBUG: Wired output via protocol.set_writer()")
            success = True
        except Exception as e:
             # print(f"DEBUG: set_writer failed: {e}")
             pass
             
    # Fallback: asyncio connection_made
    if not success and hasattr(protocol, 'connection_made'):
        try:
             protocol.connection_made(transport)
             # print("DEBUG: Wired output via protocol.connection_made()")
             success = True
        except: pass

    # Fallback: direct assignment
    if not success:
         protocol.transport = transport # Legacy/Backup
         # print("DEBUG: Wired output via protocol.transport assignment (Fallback)")


wire_server()

async def lsp_loop():
    pass

def consume_message(msg_json):
    """
    First Principles:
    The 'Protocol' object in pygls v2 is a High-Level Logic Unit.
    It does not implement 'data_received' (Low-Level Byte Stream handler) directly.
    Instead, it expects Structured Messages (Objects) or uses a decoupled Reader.
    
    Since we already have the full JSON string from JS, we don't need to simulate a Byte Stream 
    and frame it with Content-Length (Low-Level), only for pygls to unframe it again.
    
    We should Direct Inject the object.
    """
    try:
        if not server.protocol:
            logging.error("Protocol not initialized")
            return

        # 1. Parse JSON
        import json
        msg_dict = json.loads(msg_json)
        
        # 2. Structure (Validate/Convert to Pydantic Model)
        # pygls v2 uses structure_message logic
        msg_obj = server.protocol.structure_message(msg_dict)
        
        # 3. Handle (Route to Feature)
        # We need to run this on the event loop? 
        # handle_message is typically sync or returns a future?
        # Let's check signature types. Usually it schedules a task.
        server.protocol.handle_message(msg_obj)
        
    except Exception as e:
        logging.error(f"Consume Error during Direct Injection: {e}")
        import traceback
        traceback.print_exc()
