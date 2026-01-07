import type { editor } from "monaco-editor";

// Dark Theme Rules
export const TYPEDOWN_THEME_RULES_DARK: editor.ITokenThemeRule[] = [
  { token: "keyword", foreground: "FF5F56", fontStyle: "bold" },
  { token: "keyword.control", foreground: "FF5F56", fontStyle: "bold" },
  {
    token: "keyword.control.directive",
    foreground: "FF5F56",
    fontStyle: "bold",
  },
  { token: "keyword.operator", foreground: "D2A8FF" },
  { token: "storage.type", foreground: "FF5F56", fontStyle: "bold" },
  { token: "storage.modifier", foreground: "FF5F56" },

  // Entities (Classes, Types)
  { token: "entity.name.type", foreground: "27C93F" },
  { token: "entity.name.class", foreground: "27C93F" },
  { token: "entity.name.function", foreground: "79C0FF" },
  { token: "support.function", foreground: "79C0FF" },

  // Variables (Instances)
  { token: "variable.name", foreground: "E1E4E8" },
  { token: "variable.parameter", foreground: "E1E4E8" },

  // Attributes/Properties
  { token: "meta.attribute", foreground: "D2A8FF" },

  // YAML/Data Keys
  { token: "entity.name.tag", foreground: "27C93F" },

  // Strings & Values
  { token: "string", foreground: "FFBD2E" },
  { token: "string.link", foreground: "569CD6", fontStyle: "underline" },
  { token: "constant.numeric", foreground: "79C0FF" },
  { token: "constant.language", foreground: "79C0FF" },

  // Comments
  { token: "comment", foreground: "6A737D" },

  // Markdown
  { token: "markup.heading", foreground: "79C0FF", fontStyle: "bold" },
  { token: "markup.bold", fontStyle: "bold" },
  { token: "markup.italic", fontStyle: "italic" },
  { token: "markup.list", foreground: "E1E4E8" },
  { token: "markup.quote", foreground: "6A737D" },
  { token: "markup.inline.raw", foreground: "FFBD2E" },
];

// Light Theme Rules
export const TYPEDOWN_THEME_RULES_LIGHT: editor.ITokenThemeRule[] = [
  { token: "keyword", foreground: "D73A49", fontStyle: "bold" },
  { token: "keyword.control", foreground: "D73A49", fontStyle: "bold" },
  {
    token: "keyword.control.directive",
    foreground: "D73A49",
    fontStyle: "bold",
  },
  { token: "keyword.operator", foreground: "6F42C1" },
  { token: "storage.type", foreground: "D73A49", fontStyle: "bold" },
  { token: "storage.modifier", foreground: "D73A49" },

  { token: "entity.name.type", foreground: "22863A" },
  { token: "entity.name.class", foreground: "22863A" },
  { token: "entity.name.function", foreground: "6F42C1" },
  { token: "support.function", foreground: "6F42C1" },

  { token: "variable.name", foreground: "24292E" },
  { token: "variable.parameter", foreground: "24292E" },

  { token: "meta.attribute", foreground: "6F42C1" },

  { token: "entity.name.tag", foreground: "22863A" },

  { token: "string", foreground: "032F62" },
  { token: "string.link", foreground: "005CC5", fontStyle: "underline" },
  { token: "constant.numeric", foreground: "005CC5" },
  { token: "constant.language", foreground: "005CC5" },

  { token: "comment", foreground: "6A737D" },

  // Markdown
  { token: "markup.heading", foreground: "005CC5", fontStyle: "bold" },
  { token: "markup.bold", fontStyle: "bold" },
  { token: "markup.italic", fontStyle: "italic" },
  { token: "markup.list", foreground: "24292E" },
  { token: "markup.quote", foreground: "6A737D" },
  { token: "markup.inline.raw", foreground: "032F62" },
];

export const TYPEDOWN_THEME_DARK: editor.IStandaloneThemeData = {
  base: "vs-dark",
  inherit: true,
  rules: TYPEDOWN_THEME_RULES_DARK,
  colors: {
    "editor.background": "#0A0A0A",
    "editor.lineHighlightBackground": "#FFFFFF05",
  },
};

export const TYPEDOWN_THEME_LIGHT: editor.IStandaloneThemeData = {
  base: "vs",
  inherit: true,
  rules: TYPEDOWN_THEME_RULES_LIGHT,
  colors: {
    "editor.background": "#FFFFFF",
    "editor.lineHighlightBackground": "#00000005",
  },
};
