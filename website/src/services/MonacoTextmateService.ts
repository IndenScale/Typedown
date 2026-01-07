import { loadWASM, OnigScanner, OnigString } from "vscode-oniguruma";
import { Registry, INITIAL, parseRawGrammar } from "vscode-textmate";
import type { Monaco } from "@monaco-editor/react";
import type { editor } from "monaco-editor";

class MonacoTextmateService {
  private wasmLoaded = false;
  private registry: Registry | null = null;
  
  // Mapping of languageId -> scopeName
  private grammars = new Map<string, string>([
    ["typedown", "source.typedown"],
    ["python", "source.python"],
  ]);

  /**
   * Loads the Oniguruma WASM and initializes the TextMate registry.
   */
  async initialize() {
    if (this.wasmLoaded) return;

    try {
      // Load WASM
      const response = await fetch("/onig.wasm");
      if (!response.ok) {
        throw new Error(`Failed to fetch onig.wasm: ${response.statusText}`);
      }
      const data = await response.arrayBuffer();
      
      // Initialize vscode-oniguruma
      await loadWASM(data);
      this.wasmLoaded = true;

      // Initialize vscode-textmate Registry
      this.registry = new Registry({
        onigLib: Promise.resolve({
          createOnigScanner: (sources) => new OnigScanner(sources),
          createOnigString: (str) => new OnigString(str)
        }),
        loadGrammar: async (scopeName) => {
          let path = "";
          if (scopeName === "source.typedown") path = "/grammars/typedown.tmLanguage.json";
          else if (scopeName === "source.python") path = "/grammars/python.tmLanguage.json";
          else if (scopeName === "text.html.markdown") path = "/grammars/markdown.tmLanguage.json";

          if (!path) {
            console.warn(`Unknown scope name requested: ${scopeName}`);
            return null;
          }

          const res = await fetch(path);
          if (!res.ok) throw new Error(`Failed to fetch grammar ${path}: ${res.statusText}`);
          
          const content = await res.text();
          // parseRawGrammar handles both JSON and PLIST based on content/filename
          return parseRawGrammar(content, path); 
        },
      });

    } catch (e) {
      console.error("[MonacoTextmateService] Initialization failed:", e);
    }
  }

  /**
   * Injects TextMate highlighting into Monaco.
   * Note: This affects the language globally, not just a specific editor instance.
   */
  async wire(monaco: Monaco, _editor?: editor.IStandaloneCodeEditor) {
    if (!this.wasmLoaded || !this.registry) {
      await this.initialize();
    }

    if (!this.registry) return;

    // Wire up each language
    for (const [langId, scopeName] of this.grammars) {
      try {
        const grammar = await this.registry.loadGrammar(scopeName);
        if (!grammar) continue;

        // Set the tokens provider for the language
        monaco.languages.setTokensProvider(langId, {
          getInitialState: () => INITIAL,
          tokenizeEncoded: (line: string, state: any) => {
            const tokenizeLineResult2 = grammar.tokenizeLine2(line, state);
            return {
              tokens: tokenizeLineResult2.tokens,
              endState: tokenizeLineResult2.ruleStack
            };
          }
        });
      } catch (e) {
        console.error(`[MonacoTextmateService] Failed to wire grammar for ${langId}:`, e);
      }
    }
  }
}

export const textmateService = new MonacoTextmateService();