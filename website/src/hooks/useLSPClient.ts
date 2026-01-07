import { useEffect } from "react";
import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import { logger } from "@/lib/logger";
import { lspService } from "@/services/LSPService";

export function useLSPClient() {
  const { client, lspStatus, setLspStatus, setLspClient } =
    usePlaygroundStore();

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

  return lspStatus;
}