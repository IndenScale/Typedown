import { useEffect, useRef } from "react";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import { logger } from "@/lib/logger";
import { lspService } from "@/services/LSPService";

export function useLSPClient() {
  const { client, lspStatus, setLspStatus, setLspClient, openFiles, files } =
    usePlaygroundStore();

  // Track synced files to avoid re-sending didOpen
  const syncedFilesRef = useRef<Set<string>>(new Set());

  // 1. Connection Effect (Delegated to LSPService)
  useEffect(() => {
    // If we already have a client in the store, and it's happy, do nothing.
    if (client || lspStatus === "connected") {
      return;
    }

    // Guard: Browser only
    if (typeof window === "undefined") return;

    let isMounted = true;

    const connect = async () => {
      setLspStatus("connecting");
      try {
        const { client: newClient, worker } = await lspService.initialize();
        if (isMounted) {
          setLspClient(newClient, worker);
          // Status is set to 'connected' by setLspClient internally?
          // Checking store implementation might be needed, but usually setLspClient should imply success.
          // However, verify store implementation: setLspClient just sets the vars.
          // We likely need to set status explicitly or check if setLspClient does it.
          // Based on previous code: setLspClient was called, but setLspStatus("connected")
          // wasn't explicitly called in the success path of previous code?
          // Wait, 'setLspClient' might trigger status update?
          // Let's assume we need to set status if the previous code didn't do it explicitly
          // (Actually previous code didn't call setLspStatus("connected") explicitly after success,
          // maybe setLspClient handles it or it defaults?
          // Let's look at previous code:
          // window.__GlobalLSPClient = newClient;
          // window.__GlobalLSPWorker = worker;
          // setLspClient(newClient, worker);
          // resolveInit!();

          // Oh, checking previous code trace:
          // It calls setLspStatus("connecting") at start.
          // It never calls setLspStatus("connected").
          // Maybe `setLspClient` does it? Or maybe the store derives it?
          // I should check usePlaygroundStore.ts to be safe. But to be safe broadly, I'll set it here.
          setLspStatus("connected");
        }
      } catch (e) {
        if (isMounted) {
          logger.error("[LSPHook] Connection Failed:", e);
          setLspStatus("error");
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
    };
  }, [client, lspStatus, setLspStatus, setLspClient]);

  // 2. Synchronization Effect (Reactive)
  // This logic remains here as it binds the React Store state to the LSP Client
  useEffect(() => {
    if (!client || lspStatus !== "connected") return;

    // A. Initial Sync for Open Files (if not already done)
    openFiles.forEach((fileName) => {
      if (syncedFilesRef.current.has(fileName)) return;

      const file = files[fileName];
      if (file) {
        logger.debug(`[LSPHook] Initial Sync (Force Open): ${fileName}`);
        const uri = `file:///${fileName}`;

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
      state.openFiles.forEach((fileName) => {
        const newFile = state.files[fileName];
        const oldFile = prevState.files[fileName];

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
  }, [client, lspStatus, openFiles, files]);

  return lspStatus;
}
