// lsp-worker.js
// Typedown LSP Worker (ES Module)

// 1. Polyfill process for vscode-languageserver-protocol
if (typeof process === "undefined") {
  self.process = {
    env: { NODE_ENV: "production" },
    cwd: () => "/",
    platform: "web",
    version: "",
    versions: {},
    nextTick: (callback) => setTimeout(callback, 0),
  };
}

// 2. Imports
import {
  BrowserMessageReader,
  BrowserMessageWriter,
} from "https://esm.sh/vscode-languageserver-protocol@3.17.3/browser";
import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.29.0/full/pyodide.mjs";

// 3. Setup Reader/Writer
const writer = new BrowserMessageWriter(self);
const reader = new BrowserMessageReader(self);

let pyodide = null;
let isLspReady = false;
const messageQueue = [];

// 4. Initialize Pyodide & LSP
async function initPyodide() {
  console.groupCollapsed("[LSP Worker] Bootstrapping Kernel...");
  try {
    console.log("Loading Pyodide...");
    pyodide = await loadPyodide();

    console.log("Installing dependencies...");
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");

    // Install PyGLS and dependencies
    await micropip.install([
      "typing-extensions",
      "pygls>=2.0.0",
      "pydantic>=2.0.0",
      "packaging",
    ]);

    // Install Typedown Wheel
    const wheelName = "typedown-0.0.0-py3-none-any.whl";
    const wheelUrl = new URL(`/${wheelName}`, self.location.origin).href;
    console.log(`Fetching wheel: ${wheelUrl}`);

    const wheelResp = await fetch(wheelUrl);
    if (!wheelResp.ok)
      throw new Error(`Failed to fetch wheel: ${wheelResp.status}`);

    const wheelBuffer = await wheelResp.arrayBuffer();
    const mountPath = `/tmp/${wheelName}`;
    pyodide.FS.writeFile(mountPath, new Uint8Array(wheelBuffer));
    await micropip.install(`emfs:${mountPath}`);

    // 5. Fetch and Run LSP Server Script
    const serverScriptUrl = new URL("/lsp-server.py", self.location.origin).href;
    console.log(`Fetching server script: ${serverScriptUrl}`);

    const scriptResp = await fetch(serverScriptUrl);
    if (!scriptResp.ok)
      throw new Error(`Failed to fetch lsp-server.py: ${scriptResp.status}`);

    const pythonScript = await scriptResp.text();

    // Expose callback for Python -> JS communication
    self.post_lsp_message = (msg) => {
      try {
        const jsonObj = JSON.parse(msg);
        writer.write(jsonObj);
      } catch (e) {
        console.error("[LSP Worker] Failed to parse LSP response:", e);
      }
    };

    await pyodide.runPythonAsync(pythonScript);
    console.groupEnd();
    console.log("🚀 [LSP Worker] Typedown Kernel Ready.");
  } catch (e) {
    console.groupEnd();
    console.error("❌ [LSP Worker] Initialization Failed:", e);
    throw e;
  }
}

// 5. Message Handling
reader.listen((message) => {
  if (!isLspReady) {
    messageQueue.push(message);
    return;
  }
  processMessage(message);
});

function processMessage(message) {
  // Sync TextDocument updates to Virtual FS
  if (
    (message.method === "textDocument/didOpen" ||
      message.method === "typedown/syncFile") &&
    message.params
  ) {
    const { textDocument } = message.params;
    if (textDocument) {
      const { uri, text } = textDocument;
      let filePath = uri;

      // Basic URI cleanup
      if (uri.startsWith("file://")) {
        try {
          filePath = new URL(uri).pathname;
        } catch {
          /* fallback */
        }
      }

      // Ensure directory exists
      const dir = filePath.substring(0, filePath.lastIndexOf("/"));
      if (dir && dir !== "/") {
        try {
          pyodide.FS.mkdirTree(dir);
        } catch {
          /* ignore if exists */
        }
      }

      try {
        pyodide.FS.writeFile(filePath, text, { encoding: "utf8" });
        // Don't forward internal syncFile messages to Python
        if (message.method === "typedown/syncFile") return;
      } catch (e) {
        console.error(`[LSP Worker] FS Sync Error for ${filePath}:`, e);
      }
    }
  }

  // Handle FS Reset
  if (message.method === "typedown/resetFileSystem") {
    try {
      pyodide.runPython(`
import shutil
import os
import logging
keep = {'.', '..', 'tmp', 'home', 'dev', 'proc', 'lib', 'bin', 'etc', 'usr', 'var', 'sys'}
for item in os.listdir('/'):
    if item not in keep:
        path = os.path.join('/', item)
        try:
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
        except Exception as e:
            logging.error(f"Failed to clean {path}: {e}")
`);
    } catch (e) {
      console.error("[LSP Worker] FS Reset Failed:", e);
    }
    return;
  }

  // Forward to Python LSP
  try {
    const msgStr = JSON.stringify(message);
    pyodide.globals.get("consume_message")(msgStr);
  } catch (e) {
    console.error("[LSP Worker] Error passing message to Pyodide:", e);
  }
}

// Start
initPyodide().then(async () => {
  isLspReady = true;
  if (messageQueue.length > 0) {
    for (const msg of messageQueue) {
      processMessage(msg);
    }
    messageQueue.length = 0;
  }
});
