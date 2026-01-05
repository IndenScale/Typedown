// No changes needed for replacement content here, just updating the thought process.
// I will apply the polyfill in the first tool call.
// This is a dummy call to correct my reasoning, but I can't issue an empty replacement.
// I will just add a console log to signal start.
console.log("LSP Worker Starting (ESM)...");

// Polyfill process for vscode-languageserver-protocol (and other node-likes)
// Check if process exists, if not, create a minimal shim
if (typeof process === "undefined") {
  self.process = {
    env: {
      NODE_ENV: "production",
    },
    cwd: () => "/",
    platform: "web",
    version: "",
    versions: {},
    nextTick: (callback) => setTimeout(callback, 0),
  };
}

import {
  BrowserMessageReader,
  BrowserMessageWriter,
} from "https://esm.sh/vscode-languageserver-protocol@3.17.3/browser";

import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.mjs";

// Type definitions
// declare let loadPyodide: any;
let pyodide = null;
let writer;
let reader;

// Initialize Reader/Writer for LSP communication
// We use 'self' which implements AbstractMessageReader/Writer interface via postMessage
writer = new BrowserMessageWriter(self);
reader = new BrowserMessageReader(self);

// Bridge: Python -> JS (Writer)
function sendFilesToJS(data) {
  // Implement if needed
}

// Ensure Typedown's async loop doesn't block
// Pygls by default runs on asyncio.

const PYTHON_LSP_SCRIPT = `
import sys
import os
import asyncio
import json
import logging
from types import ModuleType

# Set CWD to root so we can find the files written to /world etc.
os.chdir("/")
print(f"DEBUG: CWD changed to: {os.getcwd()}")

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

# Check version robustly
try:
    from importlib.metadata import version
    ver = version("pygls")
    print(f"DEBUG: Python Kernel 3, pygls version: {ver}")
except:
    print("DEBUG: Python Kernel 3, pygls version: unknown")

# Redirect stdout/stderr
class JSWriter:
    def write(self, message):
        import js
        js.console.log(message)
    def flush(self): pass

sys.stdout = JSWriter()
sys.stderr = JSWriter()

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
            parts = msg_str.split('\\r\\n\\r\\n', 1)
            
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
            print(f"Transport Write Error: {e}")

# =========================================================
#  Wiring
# =========================================================

# =========================================================
#  Wiring
# =========================================================

transport = WebTransport()

def wire_server():
    # 1. Ensure Protocol is Initialized
    if server.protocol is None:
        print("DEBUG: server.protocol is None. Manually initializing LanguageServerProtocol...")
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
            print("DEBUG: Wired output via protocol.set_writer()")
            success = True
        except Exception as e:
             print(f"DEBUG: set_writer failed: {e}")
             
    # Fallback: asyncio connection_made
    if not success and hasattr(protocol, 'connection_made'):
        try:
             protocol.connection_made(transport)
             print("DEBUG: Wired output via protocol.connection_made()")
             success = True
        except: pass

    # Fallback: direct assignment
    if not success:
         protocol.transport = transport # Legacy/Backup
         print("DEBUG: Wired output via protocol.transport assignment (Fallback)")


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
            print("ERROR: Protocol not initialized")
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
        print(f"Consume Error during Direct Injection: {e}")
        import traceback
        traceback.print_exc()

`;

async function initPyodide() {
  console.log("Loading Pyodide...");
  pyodide = await loadPyodide();

  console.log("Installing dependencies...");
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");

  // Force pygls version to be modern and predictable
  await micropip.install([
    "typing-extensions",
    "pygls>=2.0.0",
    "pydantic>=2.0.0",
    "packaging",
  ]);

  // Install our built wheel
  // We fetch manually to better handle 404s and explicit caching/loading issues
  const wheelName = "typedown-0.0.0-py3-none-any.whl";
  const wheelUrl = new URL(`/${wheelName}`, self.location.origin).href;

  console.log(`[LSP Worker] Fetching wheel from: ${wheelUrl}`);
  const response = await fetch(wheelUrl);

  if (!response.ok) {
    const text = await response.text();
    console.error(
      `[LSP Worker] Failed to fetch wheel: ${response.status} ${response.statusText}`,
      text.slice(0, 200)
    );
    throw new Error(`Failed to fetch Typedown wheel: ${response.status}`);
  }

  const buffer = await response.arrayBuffer();
  const mountPath = `/tmp/${wheelName}`;

  console.log(
    `[LSP Worker] Writing ${buffer.byteLength} bytes to virtual FS: ${mountPath}`
  );
  pyodide.FS.writeFile(mountPath, new Uint8Array(buffer));

  console.log("[LSP Worker] Installing from virtual FS...");
  await micropip.install(`emfs:${mountPath}`);

  console.log("Running LSP Script...");

  // Expose callback for Python to send message back to JS
  self.post_lsp_message = (msg) => {
    // Parse back to JSON object if possible, or send as is?
    // BrowserMessageWriter expects an object (Message).
    try {
      const jsonObj = JSON.parse(msg);
      writer.write(jsonObj);
    } catch (e) {
      console.error("Failed to parse LSP response from Python:", msg);
    }
  };

  await pyodide.runPythonAsync(PYTHON_LSP_SCRIPT);
  console.log("Typedown Kernel Ready.");
}

const messageQueue = [];
let isLspReady = false;

// Handle incoming messages from Client (Monaco)
reader.listen((message) => {
  if (!isLspReady) {
    // Buffer messages until LSP is fully ready
    messageQueue.push(message);
    return;
  }
  processMessage(message);
});

function processMessage(message) {
  // Intercept textDocument/didOpen to sync with Pyodide FS
  if (
    (message.method === "textDocument/didOpen" ||
      message.method === "typedown/syncFile") &&
    message.params
  ) {
    // Determine params structure (didOpen has textDocument, syncFile might just be the body)
    // We normalize usage: params = { textDocument: { uri, text } } for both
    const { textDocument } = message.params;
    if (textDocument) {
      const { uri, text } = textDocument;

      // Convert URI to path (assuming file:/// schema)
      // We treat the root as / regardless of the complex URI logic for now
      // Simpler: just take the pathname.
      // Helper: ensure directory exists
      const ensureDir = (filePath) => {
        const dir = filePath.substring(0, filePath.lastIndexOf("/"));
        if (dir && dir !== "/") {
          try {
            pyodide.FS.mkdirTree(dir);
          } catch (e) {
            // Ignore if exists
          }
        }
      };

      try {
        // Robust URI parsing
        let filePath = uri;
        if (uri.startsWith("file://")) {
          const url = new URL(uri);
          filePath = url.pathname;
        }

        // Handle "phantom" slash if needed, but usually pathname starts with /
        // e.g. /world/laws.td

        ensureDir(filePath);

        // Only log if it's explicit sync to avoid spam
        if (message.method === "typedown/syncFile") {
          // console.log(`[LSP Worker] Explicit Sync to FS: ${filePath}`);
        } else {
          console.log(`[LSP Worker] didOpen Sync to FS: ${filePath}`);
        }

        pyodide.FS.writeFile(filePath, text, { encoding: "utf8" });

        // If it was a control message, STOP here. Do not propagate "typedown/syncFile" to Python.
        if (message.method === "typedown/syncFile") return;
      } catch (e) {
        console.error(
          `[LSP Worker] Failed to sync content to FS for ${uri}`,
          e
        );
      }
    }
  }

  // msg is a JSON-RPC object (Request/Notification)
  const msgStr = JSON.stringify(message);

  // Pass to Python
  try {
    pyodide.globals.get("consume_message")(msgStr);
  } catch (e) {
    console.error("Error passing message to Pyodide:", e);
  }
}

initPyodide().then(async () => {
  isLspReady = true;
  console.log(
    `[LSP Worker] Flushing ${messageQueue.length} buffered messages...`
  );
  for (const msg of messageQueue) {
    processMessage(msg);
  }
  messageQueue.length = 0; // Clear queue
});
