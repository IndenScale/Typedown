"use client";

import { usePlaygroundStore } from "@/store/usePlaygroundStore";
import Editor, { Monaco } from "@monaco-editor/react";
import { useTheme } from "next-themes";
import { X, FileCode2 } from "lucide-react";
import clsx from "clsx";
import { useEffect, useRef } from "react";

export function PlaygroundEditor() {
  const {
    activeFileName,
    files,
    updateFileContent,
    openFiles,
    openFile: selectFile,
    closeFile,
    lspStatus,
  } = usePlaygroundStore();

  const activeFile = activeFileName ? files[activeFileName] : undefined;

  const { resolvedTheme } = useTheme();

  // Store editor instance for triggering refresh
  const editorRef = useRef<any>(null);
  const monacoRef = useRef<Monaco | null>(null);

  // Note: LSP Client is now managed globally in RootLayout via <GlobalLSPManager />

  function handleEditorWillMount(monaco: Monaco) {
    console.log("[PlaygroundEditor] handleEditorWillMount called");

    // Register Typedown language
    if (
      !monaco.languages.getLanguages().some((l: any) => l.id === "typedown")
    ) {
      monaco.languages.register({ id: "typedown" });
      console.log("[PlaygroundEditor] Typedown language registered");
    }

    // Configure Monarch tokenizer for Typedown
    monaco.languages.setMonarchTokensProvider("typedown", {
      tokenizer: {
        root: [
          // Headers
          [/^#\s.*$/, "keyword.directive"],
          // Code block markers
          [/^```(model|entity|spec|config).*$/, "keyword.control"],
          [/^```$/, "keyword.control"],
          // Entity/Model/Spec declarations
          [/\b(model|entity|spec|config):\s*\w+/, "type.identifier"],
          // Python keywords (for code blocks)
          [
            /\b(class|def|if|else|elif|return|raise|import|from|pass|assert|try|except|finally|with|as|for|in|while|break|continue)\b/,
            "keyword",
          ],
          // Python types
          [
            /\b(BaseModel|str|int|float|bool|list|dict|tuple|set|None|True|False)\b/,
            "type",
          ],
          // Decorators
          [/@\w+/, "annotation"],
          // Strings
          [/"([^"\\]|\\.)*$/, "string.invalid"],
          [/"/, "string", "@string_double"],
          [/'([^'\\]|\\.)*$/, "string.invalid"],
          [/'/, "string", "@string_single"],
          // Numbers
          [/\d+\.\d+/, "number.float"],
          [/\d+/, "number"],
          // Comments
          [/#.*$/, "comment"],
          // Wiki-style references
          [/\[\[.*?\]\]/, "string.link"],
          // Keys (YAML-style)
          [/^\s*\w+:/, "variable.name"],
        ],
        string_double: [
          [/[^\\"]+/, "string"],
          [/\\./, "string.escape"],
          [/"/, "string", "@pop"],
        ],
        string_single: [
          [/[^\\']+/, "string"],
          [/\\./, "string.escape"],
          [/'/, "string", "@pop"],
        ],
      },
    });

    console.log("[PlaygroundEditor] Monarch tokenizer configured");

    // CRITICAL: Manually register Semantic Tokens Provider
    // This ensures the provider is available even if LSP connects after editor mounts
    // Use a global flag to prevent duplicate registration
    if (!(window as any).__typedownSemanticTokensProviderRegistered) {
      console.log("[PlaygroundEditor] Registering Semantic Tokens Provider...");

      monaco.languages.registerDocumentSemanticTokensProvider("typedown", {
        getLegend: () => {
          return {
            tokenTypes: ["class", "variable", "property", "struct"],
            tokenModifiers: ["declaration", "definition"],
          };
        },
        provideDocumentSemanticTokens: async (
          model: any,
          lastResultId: any,
          token: any
        ) => {
          const client = usePlaygroundStore.getState().client;
          if (!client) {
            console.log("[SemanticTokensProvider] LSP Client not ready");
            return null;
          }

          try {
            const uri = model.uri.toString();
            console.log("[SemanticTokensProvider] Requesting tokens for:", uri);

            const result = await client.sendRequest(
              "textDocument/semanticTokens/full",
              {
                textDocument: { uri },
              }
            );

            console.log("[SemanticTokensProvider] Tokens received:", result);
            return result as any;
          } catch (e) {
            console.error("[SemanticTokensProvider] Error:", e);
            return null;
          }
        },
        releaseDocumentSemanticTokens: (resultId: any) => {
          // No-op
        },
      });

      (window as any).__typedownSemanticTokensProviderRegistered = true;
      console.log(
        "[PlaygroundEditor] Semantic Tokens Provider manually registered"
      );
    } else {
      console.log(
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
    });

    monaco.editor.defineTheme("typedown-light", {
      base: "vs",
      inherit: true,
      rules: [], // Rely purely on LSP Semantic Tokens
      colors: {
        "editor.background": "#FFFFFF",
        "editor.lineHighlightBackground": "#00000005",
      },
    });
  }

  function handleEditorDidMount(editor: any, monaco: Monaco) {
    // Store references for later use
    editorRef.current = editor;
    monacoRef.current = monaco;

    console.log("[PlaygroundEditor] Editor mounted, LSP status:", lspStatus);

    // Expose global debug function
    (window as any).__debugRefreshSemanticTokens = () => {
      const model = editor.getModel();
      if (!model) {
        console.error("[Debug] No model available");
        return;
      }

      console.log("[Debug] Manually triggering Semantic Tokens refresh...");
      console.log("[Debug] Model language:", model.getLanguageId());
      console.log("[Debug] Model URI:", model.uri.toString());

      // Check if Semantic Tokens Provider is registered
      const providers = (monaco.languages as any)
        .DocumentSemanticTokensProvider;
      console.log("[Debug] Semantic Tokens Providers:", providers);

      // Try to get providers for this language
      const languageId = model.getLanguageId();
      console.log("[Debug] Checking providers for language:", languageId);

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
      console.log("[Debug] Refresh complete. Check if LSP was called.");
    };

    console.log(
      "[PlaygroundEditor] Debug function available: window.__debugRefreshSemanticTokens()"
    );

    // If LSP is already connected when editor mounts, trigger refresh immediately
    if (lspStatus === "connected") {
      const model = editor.getModel();
      if (model) {
        console.log(
          "[PlaygroundEditor] LSP already connected on mount. Triggering immediate refresh..."
        );
        setTimeout(() => {
          // Use the same strategy as in useEffect
          const currentLanguage = model.getLanguageId();
          console.log("[PlaygroundEditor] Current language:", currentLanguage);
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

          console.log("[PlaygroundEditor] Initial model refresh completed.");
        }, 150);
      }
    }

    console.log(
      "[PlaygroundEditor] Editor setup complete (using Monarch tokenizer)"
    );
  }

  // Critical Fix: Force Semantic Tokens refresh when LSP becomes ready
  // This solves the race condition where Monaco Editor mounts before LSP providers are registered
  useEffect(() => {
    // Guard: Only proceed if LSP is connected AND editor is mounted
    if (lspStatus !== "connected") {
      console.log(
        `[PlaygroundEditor] LSP not ready yet (status: ${lspStatus})`
      );
      return;
    }

    if (!editorRef.current || !monacoRef.current) {
      console.log(
        "[PlaygroundEditor] Editor not mounted yet, skipping refresh"
      );
      return;
    }

    const editor = editorRef.current;
    const monaco = monacoRef.current;
    const model = editor.getModel();

    if (!model) {
      console.log("[PlaygroundEditor] No model available, skipping refresh");
      return;
    }

    console.log(
      `[PlaygroundEditor] LSP connected + Editor ready. Triggering Semantic Tokens refresh for: ${activeFileName}`
    );

    // Strategy: Force Monaco to re-request Semantic Tokens
    // Since we manually registered the provider, Monaco should call it automatically
    // We just need to trigger a refresh
    setTimeout(async () => {
      const currentLanguage = model.getLanguageId();
      console.log(
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

      console.log(
        "[PlaygroundEditor] Refresh complete. Monaco should now call our Semantic Tokens Provider."
      );
    }, 200); // Slightly longer delay to ensure LSP is fully ready
  }, [lspStatus, activeFileName]); // Re-run when LSP status changes OR active file changes

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
          <Editor
            height="100%"
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
            }}
            path={activeFile.name}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-500 text-sm">
            <div className="text-center">
              <p className="mb-2">No file is open.</p>
              <p className="text-xs opacity-60">
                Select a file from the explorer to start editing.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
