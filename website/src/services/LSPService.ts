import { MonacoLanguageClient } from "monaco-languageclient";
import {
  BrowserMessageReader,
  BrowserMessageWriter,
} from "vscode-languageserver-protocol/browser";
import { logger } from "@/lib/logger";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";

// Polyfill Enums
const CloseAction = { DoNotRestart: 1, Restart: 2 } as const;
const ErrorAction = { Continue: 1, Shutdown: 2 } as const;

export class LSPService {
  private static instance: LSPService;

  private constructor() {}

  public static getInstance(): LSPService {
    if (!LSPService.instance) {
      LSPService.instance = new LSPService();
    }
    return LSPService.instance;
  }

  /**
   * Initializes the LSP Client and Worker.
   * Uses global singletons (window object) to survive HMR in development.
   */
  public async initialize(): Promise<{
    client: MonacoLanguageClient;
    worker: Worker;
  }> {
    if (typeof window === "undefined") {
      throw new Error("LSPService cannot be initialized on the server.");
    }

    // 1. Check for existing global instance (HMR survival)
    if (window.__GlobalLSPClient && window.__GlobalLSPWorker) {
      logger.debug(
        "[LSPService] Global client already active. Reusing instance."
      );
      return {
        client: window.__GlobalLSPClient,
        worker: window.__GlobalLSPWorker,
      };
    }

    // 2. Prevent race conditions with a global initialization promise
    if (window.__GlobalInitPromise) {
      logger.debug(
        "[LSPService] Initialization already in progress. Waiting..."
      );
      await window.__GlobalInitPromise;
      if (window.__GlobalLSPClient && window.__GlobalLSPWorker) {
        return {
          client: window.__GlobalLSPClient,
          worker: window.__GlobalLSPWorker,
        };
      }
      throw new Error(
        "Concurrent initialization completed but client/worker are missing."
      );
    }

    // 3. Start Initialization
    let resolveInit: () => void;
    let rejectInit: (e: unknown) => void;
    window.__GlobalInitPromise = new Promise((res, rej) => {
      resolveInit = res;
      rejectInit = rej;
    });

    try {
      logger.debug("[LSPService] Starting Initialization...");

      // A. VS Code API Wrapper (Singleton)
      if (!window.__GlobalVscodeApiInitialized) {
        // Dynamic import to avoid SSR issues
        const { MonacoVscodeApiWrapper } = await import(
          "monaco-languageclient/vscodeApiWrapper"
        );
        const wrapper = new MonacoVscodeApiWrapper({
          $type: "classic",
          logLevel: 0,
          viewsConfig: { $type: "EditorService" },
        } as any); // eslint-disable-line @typescript-eslint/no-explicit-any
        await wrapper.start();
        window.__GlobalVscodeApiInitialized = true;
        logger.debug("[LSPService] VS Code API Wrapper Initialized.");
      }

      // B. Create Worker
      const workerUrl = `/lsp-worker.js?v=${Date.now()}`;
      const worker = new Worker(new URL(workerUrl, window.location.origin), {
        type: "module",
      });

      // C. Configure Client
      const reader = new BrowserMessageReader(worker);
      const writer = new BrowserMessageWriter(worker);

      const client = new MonacoLanguageClient({
        name: "Typedown Browser Client",
        clientOptions: {
          documentSelector: [{ language: "typedown" }],
          errorHandler: {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            error: () => ({ action: ErrorAction.Continue as any }),
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            closed: () => ({ action: CloseAction.DoNotRestart as any }),
          },
          synchronize: {
            configurationSection: "typedown",
          },
                  initializationOptions: {
                    semanticTokens: true,
                    mode: "memory",
                  },
          
        },
        messageTransports: { reader, writer },
      });

      // Capture diagnostics for global store
      client.onNotification("textDocument/publishDiagnostics", (params) => {
        // The types are compatible but strict check might fail on minor version mismatch
        usePlaygroundStore.getState().setDiagnostics(params.uri, params.diagnostics);
      });

      // D. Start Client
      logger.debug("[LSPService] Starting Client...");
      await client.start();
      logger.debug("[LSPService] Client Connected.");
      
      // E. Initial Project Load (Full Snapshot)
      this.loadCurrentProject(client);

      // F. Save to Globals
      window.__GlobalLSPClient = client;
      window.__GlobalLSPWorker = worker;

      resolveInit!();
      return { client, worker };
    } catch (e) {
      window.__GlobalInitPromise = undefined; // Clear lock on failure
      rejectInit!(e);
      logger.error("[LSPService] Initialization Failed:", e);
      throw e;
    }
  }
  
  private loadCurrentProject(client: MonacoLanguageClient) {
    const currentState = usePlaygroundStore.getState();
    const filesPayload: Array<{ uri: string; content: string }> = [];

    // Send ALL files, not just open ones
    Object.entries(currentState.files).forEach(([, file]) => {
      // Ensure logical path (simple mapping for playground)
      const logicalPath = file.path || `/${file.name}`;
      const uri = `file://${logicalPath}`;
      filesPayload.push({
        uri,
        content: file.content || "",
      });
    });

    logger.debug(
      `[LSPService] Loading project with ${filesPayload.length} files.`
    );
    client.sendNotification("typedown/loadProject", { files: filesPayload });
  }
}

export const lspService = LSPService.getInstance();