"use client";

import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import Editor, { Monaco } from "@monaco-editor/react";
import type * as MonacoTypes from "monaco-editor";
import { useTheme } from "next-themes";
import { X, FileCode2 } from "lucide-react";
import clsx from "clsx";
import { useEffect, useRef } from "react";
import { logger } from "@/lib/logger";
import { MarkdownPreview } from "./MarkdownPreview";
import { textmateService } from "@/services/MonacoTextmateService";

import { useTranslation } from "./TranslationContext";

export function PlaygroundEditor() {
  const {
    activeFileName,
    files,
    updateFileContent,
    openFiles,
    openFile: selectFile,
    closeFile,
    lspStatus,
    diagnostics,
  } = usePlaygroundStore();

  const activeFile = activeFileName ? files[activeFileName] : undefined;

  const { resolvedTheme } = useTheme();

  // Store editor instance for triggering refresh
  const editorRef = useRef<MonacoTypes.editor.IStandaloneCodeEditor | null>(
    null
  );
  const monacoRef = useRef<Monaco | null>(null);
  const t = useTranslation();

  // Note: LSP Client is now managed globally in RootLayout via <GlobalLSPManager />

  function handleEditorWillMount(monaco: Monaco) {
    logger.debug("[PlaygroundEditor] handleEditorWillMount called");

    // Register Typedown language
    if (
      !monaco.languages
        .getLanguages()
        .some((l: { id: string }) => l.id === "typedown")
    ) {
      monaco.languages.register({ id: "typedown" });
      logger.debug("[PlaygroundEditor] Typedown language registered");
    }

    // Configure Monarch tokenizer for Typedown
    // REMOVED: Switched to TextMate grammar via textmateService

    logger.debug("[PlaygroundEditor] Monarch tokenizer configured");

    // CRITICAL: Manually register Semantic Tokens Provider
    // This ensures the provider is available even if LSP connects after editor mounts
    // Use a global flag to prevent duplicate registration
    if (!window.__typedownSemanticTokensProviderRegistered) {
      logger.debug(
        "[PlaygroundEditor] Registering Semantic Tokens Provider..."
      );

      monaco.languages.registerDocumentSemanticTokensProvider("typedown", {
        getLegend: () => {
          return {
            tokenTypes: ["class", "variable", "property", "struct"],
            tokenModifiers: ["declaration", "definition"],
          };
        },
        provideDocumentSemanticTokens: async (
          model: MonacoTypes.editor.ITextModel,
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          _lastResultId: string | null,
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          _token: MonacoTypes.CancellationToken
        ) => {
          const client = usePlaygroundStore.getState().client;
          if (!client) {
            logger.debug("[SemanticTokensProvider] LSP Client not ready");
            return null;
          }

          try {
            const uri = model.uri.toString();
            logger.debug(
              "[SemanticTokensProvider] Requesting tokens for:",
              uri
            );

            const result = await client.sendRequest(
              "textDocument/semanticTokens/full",
              {
                textDocument: { uri },
              }
            );

            logger.debug("[SemanticTokensProvider] Tokens received:", result);
            return result as MonacoTypes.languages.SemanticTokens;
          } catch (e) {
            logger.error("[SemanticTokensProvider] Error:", e);
            return null;
          }
        },
        releaseDocumentSemanticTokens: (
          // eslint-disable-next-line @typescript-eslint/no-unused-vars
          _resultId: string | undefined
        ) => {
          // No-op
        },
      });

      window.__typedownSemanticTokensProviderRegistered = true;
      logger.debug(
        "[PlaygroundEditor] Semantic Tokens Provider manually registered"
      );
    } else {
      logger.debug(
        "[PlaygroundEditor] Semantic Tokens Provider already registered, skipping"
      );
    }

    // Define Themes
    // We map both specific TextMate scopes AND generic Semantic Token types
    monaco.editor.defineTheme("typedown-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [], // Rely purely on LSP Semantic Tokens
      colors: {
        "editor.background": "#0A0A0A",
        "editor.lineHighlightBackground": "#FFFFFF05",
      },
    } as MonacoTypes.editor.IStandaloneThemeData);

    monaco.editor.defineTheme("typedown-light", {
      base: "vs",
      inherit: true,
      rules: [], // Rely purely on LSP Semantic Tokens
      colors: {
        "editor.background": "#FFFFFF",
        "editor.lineHighlightBackground": "#00000005",
      },
    } as MonacoTypes.editor.IStandaloneThemeData);
  }

  function handleEditorDidMount(
    editor: MonacoTypes.editor.IStandaloneCodeEditor,
    monaco: Monaco
  ) {
    // Store references for later use
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Wire TextMate grammar
    textmateService.wire(monaco, editor).then(() => {
      logger.debug("[PlaygroundEditor] TextMate grammar wired");
    });

    logger.debug("[PlaygroundEditor] Editor mounted, LSP status:", lspStatus);

    // Expose global debug function
    window.__debugRefreshSemanticTokens = () => {
      const model = editor.getModel();
      if (!model) {
        logger.error("[Debug] No model available");
        return;
      }

      logger.debug("[Debug] Manually triggering Semantic Tokens refresh...");
      logger.debug("[Debug] Model language:", model.getLanguageId());
      logger.debug("[Debug] Model URI:", model.uri.toString());

      // Check if Semantic Tokens Provider is registered
      // LINT EXCEPTION: Accessing internal API for debugging purposes
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const providers = (monaco.languages as any)
        .DocumentSemanticTokensProvider;
      logger.debug("[Debug] Semantic Tokens Providers:", providers);

      // Try to get providers for this language
      const languageId = model.getLanguageId();
      logger.debug("[Debug] Checking providers for language:", languageId);

      const currentLanguage = model.getLanguageId();
      monaco.editor.setModelLanguage(model, currentLanguage);
      editor.layout();

      const position = editor.getPosition();
      editor.executeEdits("", [
        { range: new monaco.Range(1, 1, 1, 1), text: " " },
      ]);
      editor.executeEdits("", [
        { range: new monaco.Range(1, 1, 1, 2), text: "" },
      ]);
      if (position) {
        editor.setPosition(position);
      }
      logger.debug("[Debug] Refresh complete. Check if LSP was called.");
    };

    logger.debug(
      "[PlaygroundEditor] Debug function available: window.__debugRefreshSemanticTokens()"
    );

    // If LSP is already connected when editor mounts, trigger refresh immediately
    if (lspStatus === "connected") {
      const model = editor.getModel();
      if (model) {
        logger.debug(
          "[PlaygroundEditor] LSP already connected on mount. Triggering immediate refresh..."
        );
        setTimeout(() => {
          // Use the same strategy as in useEffect
          const currentLanguage = model.getLanguageId();
          logger.debug("[PlaygroundEditor] Current language:", currentLanguage);
          monaco.editor.setModelLanguage(model, currentLanguage);
          editor.layout();

          const position = editor.getPosition();
          editor.executeEdits("", [
            { range: new monaco.Range(1, 1, 1, 1), text: " " },
          ]);
          editor.executeEdits("", [
            { range: new monaco.Range(1, 1, 1, 2), text: "" },
          ]);
          if (position) {
            editor.setPosition(position);
          }

          logger.debug("[PlaygroundEditor] Initial model refresh completed.");
        }, 150);
      }
    }

    logger.debug(
      "[PlaygroundEditor] Editor setup complete (using Monarch tokenizer)"
    );
  }

  // Critical Fix: Force Semantic Tokens refresh when LSP becomes ready
  // This solves the race condition where Monaco Editor mounts before LSP providers are registered
  useEffect(() => {
    // Guard: Only proceed if LSP is connected AND editor is mounted
    if (lspStatus !== "connected") {
      logger.debug(
        `[PlaygroundEditor] LSP not ready yet (status: ${lspStatus})`
      );
      return;
    }

    if (!editorRef.current || !monacoRef.current) {
      logger.debug(
        "[PlaygroundEditor] Editor not mounted yet, skipping refresh"
      );
      return;
    }

    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor.getModel();

    if (!model) {
      logger.debug("[PlaygroundEditor] No model available, skipping refresh");
      return;
    }

    logger.debug(
      `[PlaygroundEditor] LSP connected + Editor ready. Triggering Semantic Tokens refresh for: ${activeFileName}`
    );

    // Strategy: Force Monaco to re-request Semantic Tokens
    // Since we manually registered the provider, Monaco should call it automatically
    // We just need to trigger a refresh
    setTimeout(async () => {
      const currentLanguage = model.getLanguageId();
      logger.debug(
        "[PlaygroundEditor] Triggering refresh for language:",
        currentLanguage
      );

      // Method 1: Force model language re-assignment (triggers all providers)
      monaco.editor.setModelLanguage(model, currentLanguage);

      // Method 2: Trigger editor layout recalculation
      editor.layout();

      // Method 3: Force a small edit and undo (guaranteed to trigger providers)
      const position = editor.getPosition();
      editor.executeEdits("", [
        {
          range: new monaco.Range(1, 1, 1, 1),
          text: " ",
        },
      ]);
      editor.executeEdits("", [
        {
          range: new monaco.Range(1, 1, 1, 2),
          text: "",
        },
      ]);
      if (position) {
        editor.setPosition(position);
      }

      logger.debug(
        "[PlaygroundEditor] Refresh complete. Monaco should now call our Semantic Tokens Provider."
      );
    }, 200); // Slightly longer delay to ensure LSP is fully ready
  }, [lspStatus, activeFileName]); // Re-run when LSP status changes OR active file changes

  // Sync Diagnostics to Monaco Markers
  useEffect(() => {
    if (!monacoRef.current || !editorRef.current || !activeFileName) return;

    const monaco = monacoRef.current;
    const editor = editorRef.current;
    const model = editor.getModel();

    if (!model) return;

    // The store uses params.uri from the server (file:///...)
    // Monaco model.uri.toString() should match this.
    const activeFileUri = model.uri.toString();
    const fileDiagnostics = diagnostics[activeFileUri] || [];

    logger.debug(
      `[PlaygroundEditor] Syncing diagnostics for ${activeFileUri}:`,
      fileDiagnostics
    );

    const markers: MonacoTypes.editor.IMarkerData[] = fileDiagnostics.map(
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (diag: any) => ({
        severity:
          diag.severity === 1
            ? monaco.MarkerSeverity.Error
            : diag.severity === 2
            ? monaco.MarkerSeverity.Warning
            : diag.severity === 3
            ? monaco.MarkerSeverity.Info
            : monaco.MarkerSeverity.Hint,
        startLineNumber: diag.range.start.line + 1,
        startColumn: diag.range.start.character + 1,
        endLineNumber: diag.range.end.line + 1,
        endColumn: diag.range.end.character + 1,
        message: diag.message,
        source: diag.source || "typedown",
      })
    );

    monaco.editor.setModelMarkers(model, "typedown", markers);
  }, [diagnostics, activeFileName]);

  // Debounced Validation Trigger (5s inactivity)
  // This ensures heavy checks (Specs/L3) run after the user stops typing
  useEffect(() => {
    if (lspStatus !== "connected" || !activeFileName) return;

    const timer = setTimeout(() => {
      const { client } = usePlaygroundStore.getState();
      if (client) {
        logger.debug(
          "[PlaygroundEditor] Triggering delayed full validation (5s)..."
        );
        client
          .sendRequest("workspace/executeCommand", {
            command: "typedown.triggerValidation",
          })
          .catch((err) =>
            logger.error("[PlaygroundEditor] Delayed validation failed:", err)
          );
      }
    }, 5000);

    return () => clearTimeout(timer);
  }, [activeFile?.content, lspStatus, activeFileName]);

  return (
    <div className="flex h-full w-full flex-col">
      {/* Editor Tabs */}
      <div className="flex flex-none h-9 bg-gray-100 dark:bg-[#0A0A0A] border-b border-gray-200 dark:border-gray-800 overflow-x-auto no-scrollbar">
        {openFiles.map((fileName) => {
          const isActive = fileName === activeFileName;
          return (
            <div
              key={fileName}
              onClick={() => selectFile(fileName)}
              className={clsx(
                "group flex items-center min-w-[120px] max-w-[200px] px-3 py-1 cursor-pointer select-none text-xs border-r border-gray-200 dark:border-gray-800",
                isActive
                  ? "bg-white dark:bg-[#0A0A0A] text-foreground font-medium border-t-2 border-t-primary"
                  : "bg-gray-50 dark:bg-[#111] text-gray-500 hover:bg-gray-100 dark:hover:bg-[#161616]"
              )}
              style={isActive ? { borderTopColor: "#007ACC" } : {}}>
              <FileCode2 className="w-3.5 h-3.5 mr-2 opacity-70" />
              <span className="truncate flex-1">{fileName}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  closeFile(fileName);
                }}
                className={clsx(
                  "ml-1 p-0.5 rounded-sm opacity-0 group-hover:opacity-100 hover:bg-gray-200 dark:hover:bg-gray-700 transition-opacity",
                  isActive && "opacity-100"
                )}>
                <X className="w-3 h-3" />
              </button>
            </div>
          );
        })}
      </div>

      {/* Editor Area */}
      <div className="flex-1 min-h-0 relative">
        {activeFile ? (
          activeFile.language === "markdown" ? (
            <MarkdownPreview content={activeFile.content} />
          ) : (
            <Editor
              height="100%"
              path={activeFile.path || `/${activeFile.name}`} // CRITICAL FIX: Ensure Editor Model URI matches LSP Sync URI
              language={activeFile.language}
              value={activeFile.content}
              theme={
                resolvedTheme === "dark" ? "typedown-dark" : "typedown-light"
              }
              onMount={handleEditorDidMount}
              beforeMount={handleEditorWillMount}
              onChange={(value) =>
                updateFileContent(activeFile.name, value || "")
              }
              options={{
                readOnly: activeFile.readOnly,
                minimap: { enabled: false },
                scrollBeyondLastLine: true,
                fontSize: 14,
                fontFamily: 'Menlo, Monaco, "Courier New", monospace',
                wordWrap: "on",
                padding: { top: 16 },
                // CRITICAL: Enable Semantic Tokens
                "semanticHighlighting.enabled": true,
                // Enable CodeLens
                codeLens: true,
              }}
              // CRITICAL: Match the URI used by LSP Worker (Logical Path)
              // e.g. /examples/03_simple_rules/rules.td
            />
          )
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500 text-sm">
            <div className="text-center">
              <p className="mb-2">{t.editor.noFileOpen}</p>
              <p className="text-xs opacity-60">{t.editor.selectFile}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
