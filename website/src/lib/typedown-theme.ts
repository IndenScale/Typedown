import type { editor } from "monaco-editor";

// Dark Theme Rules
export const TYPEDOWN_THEME_RULES_DARK: editor.ITokenThemeRule[] = [
  { token: "keyword", foreground: "FF5F56", fontStyle: "bold" },
  { token: "keyword.control", foreground: "FF5F56", fontStyle: "bold" },
  { token: "keyword.directive", foreground: "FFFFFF", fontStyle: "bold" },
  { token: "type", foreground: "27C93F" },
  { token: "type.identifier", foreground: "27C93F" },
  { token: "string", foreground: "FFBD2E" },
  { token: "string.link", foreground: "569CD6", fontStyle: "underline" },
  { token: "comment", foreground: "6A737D" },
  { token: "variable.name", foreground: "E1E4E8" },
  { token: "number", foreground: "79C0FF" },
  { token: "annotation", foreground: "D2A8FF" },
];

// Light Theme Rules
export const TYPEDOWN_THEME_RULES_LIGHT: editor.ITokenThemeRule[] = [
  { token: "keyword", foreground: "D73A49", fontStyle: "bold" },
  { token: "keyword.control", foreground: "D73A49", fontStyle: "bold" },
  { token: "keyword.directive", foreground: "24292E", fontStyle: "bold" },
  { token: "type", foreground: "22863A" },
  { token: "type.identifier", foreground: "22863A" },
  { token: "string", foreground: "032F62" },
  { token: "string.link", foreground: "005CC5", fontStyle: "underline" },
  { token: "comment", foreground: "6A737D" },
  { token: "variable.name", foreground: "24292E" },
  { token: "number", foreground: "005CC5" },
  { token: "annotation", foreground: "6F42C1" },
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
