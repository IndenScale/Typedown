import { useEffect, useRef } from "react";
import type { MonacoLanguageClient } from "monaco-languageclient";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";

// Polyfill Enums if not exported
const CloseAction = { DoNotRestart: 1, Restart: 2 };
const ErrorAction = { Continue: 1, Shutdown: 2 };

// Global Type Definition for HMR/Persistence
declare global {
  interface Window {
    __GlobalVscodeApiInitialized?: boolean;
    __GlobalLSPClient?: MonacoLanguageClient;
    __GlobalLSPWorker?: Worker;
    __GlobalInitPromise?: Promise<void>;
  }
}

export function useLSPClient() {
  const { client, lspStatus, setLspStatus, setLspClient, openFiles, files } =
    usePlaygroundStore();

  // Track synced files to avoid re-sending didOpen
  const syncedFilesRef = useRef<Set<string>>(new Set());

  // 1. Connection Effect (Global Singleton)
  useEffect(() => {
    // If we already have a client in the store, and it's happy, do nothing.
    if (client || lspStatus === "connected") {
      return;
    }

    // Guard: Browser only
    if (typeof window === "undefined") return;

    let isMounted = true;

    const initLSP = async () => {
      // Global Init Lock
      if (window.__GlobalInitPromise) {
        console.log(
          "[LSP] Initialization already in progress (Promise locked). Waiting..."
        );
        try {
          await window.__GlobalInitPromise;
          // After waiting, check if result is success
          if (window.__GlobalLSPClient && !client) {
            const runningWorker = window.__GlobalLSPWorker;
            if (runningWorker) {
              setLspClient(window.__GlobalLSPClient, runningWorker);
            }
          }
        } catch (e) {
          console.error("Waited for init promise but it failed", e);
        }
        return;
      }

      // 0. Hard Singleton Check (The "Never Die" Policy)
      // If a global client exists and is running, we DO NOT touch it.
      // We absolutely do not want to stop it, restart it, or re-init it during HMR.
      if (window.__GlobalLSPClient) {
        console.log("[LSP] Global client already active. Skipping init.");

        // Ensure store is synced with the global instance
        // This is crucial for "Direct Refresh" scenario where Zustand store is reset
        // but Global Client persists in window object (if soft navigate)
        // OR simply hydrating the store reference.
        if (!client) {
          const runningClient = window.__GlobalLSPClient;
          const runningWorker = window.__GlobalLSPWorker;

          if (runningClient && runningWorker) {
            setLspClient(runningClient, runningWorker);
          }
        }
        return;
      }

      setLspStatus("connecting");

      // Create a promise for this initialization attempt
      let resolveInit: () => void;
      let rejectInit: (e: any) => void;
      window.__GlobalInitPromise = new Promise((res, rej) => {
        resolveInit = res;
        rejectInit = rej;
      });

      try {
        console.log("[LSP] Starting Initialization...");

        // A. VS Code API (Singleton Check - One Time Per Page Load)
        if (!window.__GlobalVscodeApiInitialized) {
          const { MonacoVscodeApiWrapper } = await import(
            "monaco-languageclient/vscodeApiWrapper"
          );
          const wrapper = new MonacoVscodeApiWrapper({
            $type: "classic",
            logLevel: 0,
            viewsConfig: { $type: "EditorService" },
          } as any);
          await wrapper.start();
          window.__GlobalVscodeApiInitialized = true;
          console.log("[LSP] VS Code API Wrapper Initialized.");
        }

        // B. Imports
        const { MonacoLanguageClient } = await import("monaco-languageclient");
        const { BrowserMessageReader, BrowserMessageWriter } = await import(
          "vscode-languageserver-protocol/browser"
        );

        // C. Worker
        const workerUrl = `/lsp-worker.js?v=${Date.now()}`;
        const worker = new Worker(new URL(workerUrl, window.location.origin), {
          type: "module",
        });

        // CRITICAL: Pre-seed the Worker FS with files *before* LSP initialization.
        // This ensures that when the Python Server starts and scans the FS, it finds the files.
        // We use raw postMessage to guarantee these messages are in the event queue
        // before the 'initialize' message that the Client will send.
        const currentState = usePlaygroundStore.getState();
        console.log(
          `[LSP] Pre-seeding ${currentState.openFiles.length} files...`
        );

        currentState.openFiles.forEach((fileName) => {
          const file = currentState.files[fileName];
          if (file) {
            const msg = {
              jsonrpc: "2.0",
              method: "typedown/syncFile",
              params: {
                textDocument: {
                  uri: `file:///${fileName}`,
                  languageId: "typedown",
                  version: 1,
                  text: file.content,
                },
              },
            };
            worker.postMessage(msg);
            // Do NOT mark as synced here.
            // We want the "Initial Sync" in the useEffect to run again once connected,
            // to ensure the latest content (post-hydration) is sent to the server.
            // syncedFilesRef.current.add(fileName);
          }
        });

        // D. Client
        const reader = new BrowserMessageReader(worker);
        const writer = new BrowserMessageWriter(worker);

        const newClient = new MonacoLanguageClient({
          name: "Typedown Browser Client",
          clientOptions: {
            documentSelector: [{ language: "typedown" }],
            errorHandler: {
              error: () => ({ action: ErrorAction.Continue as any }),
              closed: () => ({ action: CloseAction.DoNotRestart as any }),
            },
            // CRITICAL: Enable workspace configuration and synchronization
            synchronize: {
              configurationSection: "typedown",
            },
            // CRITICAL: Request Semantic Tokens capability from server
            initializationOptions: {
              semanticTokens: true,
            },
          },
          messageTransports: { reader, writer },
        });

        // E. Start Client
        console.log("[LSP] Starting Client...");
        await newClient.start(); // We trust the singleton check above to prevent duplicates

        console.log("[LSP] Client Connected.");

        // Store Globally & in Store
        window.__GlobalLSPClient = newClient;
        window.__GlobalLSPWorker = worker;
        setLspClient(newClient, worker);

        // Resolve the lock
        resolveInit!();
      } catch (e) {
        // Reject the lock
        rejectInit!(e);
        window.__GlobalInitPromise = undefined; // Clear the failed promise

        if (isMounted) {
          console.error("[LSP] Init Failed:", e);
          setLspStatus("error");
        }
      }
    };

    initLSP();

    return () => {
      isMounted = false;
      // ABSOLUTELY NO CLEANUP.
      // The client lives as long as the tab lives.
    };
  }, [client, lspStatus, setLspStatus, setLspClient]);

  // 2. Synchronization Effect (Reactive)
  // Watch openFiles and sync them if the client is ready
  useEffect(() => {
    if (!client || lspStatus !== "connected") return;

    // A. Initial Sync for Open Files (if not already done)
    openFiles.forEach((fileName) => {
      if (syncedFilesRef.current.has(fileName)) return;

      const file = files[fileName];
      if (file) {
        console.log(`[LSP] Initial Sync (Force Open): ${fileName}`);
        const uri = `file:///${fileName}`;

        // CHANGE: Use 'textDocument/didOpen' to ensure the server recognizes the file as open.
        // Previously we used 'typedown/syncFile' (FS only) to avoid duplicates,
        // but MonacoLanguageClient does not faithfully send didOpen in this Late-Init scenario.
        // By sending it explicitly here, we ensure the server starts processing features (Semantic Tokens).
        client.sendNotification("textDocument/didOpen", {
          textDocument: {
            uri: uri,
            languageId: "typedown",
            version: 1,
            text: file.content,
          },
        });

        syncedFilesRef.current.add(fileName);
      }
    });

    // B. Continuous Sync (Watch for Content Changes)
    const unsub = usePlaygroundStore.subscribe((state, prevState) => {
      // Simple diff strategy: check if content of any OPEN file changed
      // We iterate openFiles because those are the interesting ones for now
      state.openFiles.forEach((fileName) => {
        const newFile = state.files[fileName];
        const oldFile = prevState.files[fileName];

        // If content changed
        if (newFile && oldFile && newFile.content !== oldFile.content) {
          const uri = `file:///${fileName}`;
          client.sendNotification("typedown/syncFile", {
            textDocument: {
              uri: uri,
              text: newFile.content,
            },
          });
        }
      });
    });

    return () => {
      unsub();
    };
  }, [client, lspStatus, openFiles]); // Removed 'files' to avoid re-renders

  return lspStatus;
}
