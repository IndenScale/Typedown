import { loadWASM } from "vscode-oniguruma";
import { Registry } from "monaco-textmate";
import { wireTmGrammars } from "monaco-editor-textmate";
import type { Monaco } from "@monaco-editor/react";

class MonacoTextmateService {
  private wasmLoaded = false;
  private registry: Registry | null = null;
  private grammars = new Map<string, string>(); // langId -> scopeName

  constructor() {
    this.grammars.set("typedown", "source.typedown");
    // python is often embedded but can be standalone
    this.grammars.set("python", "source.python");
  }

  /**
   * Loads the Oniguruma WASM and initializes the TextMate registry.
   * This should be called once, lazily.
   */
  async initialize() {
    if (this.wasmLoaded) return;

    try {
      // Load WASM
      // Note: We assume onig.wasm is served from /public
      const response = await fetch("/onig.wasm");
      if (!response.ok) {
        throw new Error(`Failed to fetch onig.wasm: ${response.statusText}`);
      }
      const data = await response.arrayBuffer();
      await loadWASM(data);
      this.wasmLoaded = true;

      // Init Registry
      this.registry = new Registry({
        getGrammarDefinition: async (scopeName) => {
          let path = "";
          if (scopeName === "source.typedown")
            path = "/grammars/typedown.tmLanguage.json";
          else if (scopeName === "source.python")
            path = "/grammars/python.tmLanguage.json";
          else if (scopeName === "text.html.markdown")
            path = "/grammars/markdown.tmLanguage.json";

          if (!path) {
            // Fallback or error
            console.warn(`Unknown scope name requested: ${scopeName}`);
            return null as any;
          }

          const res = await fetch(path);
          if (!res.ok) {
            throw new Error(
              `Failed to fetch grammar ${path}: ${res.statusText}`
            );
          }
          const content = await res.json();
          return { format: "json", content };
        },
      });
    } catch (e) {
      console.error("[MonacoTextmateService] Initialization failed:", e);
      // We might want to set a 'failed' state so we don't retry incessantly
    }
  }

  /**
   * Injects TextMate highlighting into the given editor instance.
   */
  async wire(monaco: Monaco, editor: any) {
    if (!this.wasmLoaded || !this.registry) {
      await this.initialize();
    }

    if (this.registry) {
      try {
        await wireTmGrammars(monaco, this.registry, this.grammars, editor);
      } catch (e) {
        console.error("[MonacoTextmateService] Wiring failed:", e);
      }
    }
  }
}

export const textmateService = new MonacoTextmateService();
