import { MonacoLanguageClient } from "monaco-languageclient";

declare global {
  interface Window {
    /**
     * Tracks if the VS Code API wrapper has been initialized.
     * This must only happen once per page load.
     */
    __GlobalVscodeApiInitialized?: boolean;

    /**
     * persistent LSP Client instance for HMR.
     */
    __GlobalLSPClient?: MonacoLanguageClient;

    /**
     * Persistent Web Worker instance for HMR.
     */
    __GlobalLSPWorker?: Worker;

    /**
     * Promise generic to track initialization status and prevent race conditions.
     */
    __GlobalInitPromise?: Promise<void>;

    /**
     * Flag to prevent duplicate registration of Semantic Tokens Provider.
     */
    __typedownSemanticTokensProviderRegistered?: boolean;

    /**
     * Debug helper exposed to window for manual triggering of token refresh.
     */
    __debugRefreshSemanticTokens?: () => void;
  }
}

export {};
