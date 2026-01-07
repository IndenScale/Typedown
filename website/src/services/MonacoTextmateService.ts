import { loadWASM, OnigScanner, OnigString } from "vscode-oniguruma";
import { Registry, INITIAL, parseRawGrammar, type IRawTheme } from "vscode-textmate";
import type { Monaco } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { TYPEDOWN_THEME_RULES_DARK } from "@/lib/typedown-theme";

class MonacoTextmateService {
  private wasmLoaded = false;
  private registry: Registry | null = null;

  // Mapping of languageId -> scopeName
  private grammars = new Map<string, string>([
    ["typedown", "source.typedown"],
    ["python", "source.python"],
    ["markdown", "text.html.markdown"],
    ["yaml", "source.yaml"],
    ["html", "text.html.basic"],
    ["css", "source.css"],
    ["javascript", "source.js"],
    ["typescript", "source.ts"],
  ]);

  /**
   * Converts Monaco TokenThemeRules to TextMate IRawTheme
   */
  private generateVscodeTheme(rules: editor.ITokenThemeRule[]): IRawTheme {
    return {
      name: "Typedown Theme",
      settings: rules.map((rule) => ({
        scope: rule.token,
        settings: {
          foreground: rule.foreground ? `#${rule.foreground}` : undefined,
          fontStyle: rule.fontStyle,
        },
      })),
    };
  }

  /**
   * Loads the Oniguruma WASM and initializes the TextMate registry.
   */
  async initialize() {
    if (this.wasmLoaded) return;

    try {
      console.debug("[MonacoTextmateService] Starting initialization...");
      // Load WASM
      const response = await fetch("/onig.wasm");
      if (!response.ok) {
        throw new Error(`Failed to fetch onig.wasm: ${response.statusText}`);
      }
      const data = await response.arrayBuffer();
      console.debug("[MonacoTextmateService] onig.wasm loaded");

      // Initialize vscode-oniguruma
      await loadWASM(data);
      this.wasmLoaded = true;
      console.debug("[MonacoTextmateService] oniguruma initialized");

      // Initialize vscode-textmate Registry
      this.registry = new Registry({
        onigLib: Promise.resolve({
          createOnigScanner: (sources) => new OnigScanner(sources),
          createOnigString: (str) => new OnigString(str),
        }),
        // Pre-load theme to ensure colors are mapped correctly
        theme: this.generateVscodeTheme(TYPEDOWN_THEME_RULES_DARK), // Default to Dark for now
        loadGrammar: async (scopeName) => {
          console.debug(`[MonacoTextmateService] Loading grammar for scope: ${scopeName}`);
          let path = "";
          switch (scopeName) {
            case "source.typedown":
              path = "/grammars/typedown.tmLanguage.json";
              break;
            case "source.python":
              path = "/grammars/python.tmLanguage.json";
              break;
            case "text.html.markdown":
              path = "/grammars/markdown.tmLanguage.json";
              break;
            case "source.yaml":
              path = "/grammars/yaml.tmLanguage.json";
              break;
            case "text.html.basic":
            case "text.html.derivative": // Handle VS Code's markdown injection scope
              path = "/grammars/html.tmLanguage.json";
              break;
            case "source.css":
              path = "/grammars/css.tmLanguage.json";
              break;
            case "source.js":
              path = "/grammars/javascript.tmLanguage.json";
              break;
            case "source.ts":
            case "source.tsx":
              path = "/grammars/typescript.tmLanguage.json";
              break;
            // Add other core languages here
          }

          if (!path) {
            // Provide a dummy empty grammar for unknown scopes to prevent errors
            // and satisfy dependencies (e.g. embedded languages in Markdown)
            console.debug(
              `[MonacoTextmateService] Stubbing missing scope: ${scopeName}`
            );
            return {
              scopeName,
              patterns: [],
              repository: {},
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
            } as any;
          }

          // Add timestamp to prevent caching during development
          console.debug(`[MonacoTextmateService] Fetching grammar from: ${path}`);
          const res = await fetch(`${path}?v=${Date.now()}`);
          if (!res.ok) {
            console.error(
              `[MonacoTextmateService] Failed to fetch grammar for ${scopeName}: ${res.statusText}`
            );
            return null;
          }

          const content = await res.text();
          console.debug(`[MonacoTextmateService] Grammar loaded for ${scopeName}`);
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
  async wire(monaco: Monaco) {
    if (!this.wasmLoaded || !this.registry) {
      await this.initialize();
    }

    if (!this.registry) {
        console.error("[MonacoTextmateService] Registry not initialized, aborting wire.");
        return;
    }

    // Wire up each language
    for (const [langId, scopeName] of this.grammars) {
      try {
        const grammar = await this.registry.loadGrammar(scopeName);
        if (!grammar) {
            console.warn(`[MonacoTextmateService] Failed to load grammar for ${scopeName}`);
            continue;
        }

        // Set the tokens provider for the language
        monaco.languages.setTokensProvider(langId, {
          getInitialState: () => INITIAL,
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          tokenizeEncoded: (line: string, state: any) => {
            const tokenizeLineResult2 = grammar.tokenizeLine2(line, state);
            return {
              tokens: tokenizeLineResult2.tokens,
              endState: tokenizeLineResult2.ruleStack,
            };
          },
        });
        console.debug(`[MonacoTextmateService] Successfully wired grammar for ${langId}`);
      } catch (e) {
        console.error(
          `[MonacoTextmateService] Failed to wire grammar for ${langId}:`,
          e
        );
      }
    }
  }
}

export const textmateService = new MonacoTextmateService();
