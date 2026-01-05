import { create } from "zustand";
import type { MonacoLanguageClient } from "monaco-languageclient";
import { DEMOS } from "@/lib/demos";

interface PlaygroundFile {
  name: string;
  language: string;
  content: string;
  readOnly?: boolean;
  path?: string;
}

interface PlaygroundState {
  // File System State
  files: Record<string, PlaygroundFile>;
  openFiles: string[];
  activeFileName: string | null;

  // LSP State
  lspStatus: "disabled" | "connecting" | "connected" | "error";
  client: MonacoLanguageClient | null;
  worker: Worker | null;

  // Actions
  setFiles: (files: Record<string, PlaygroundFile>) => void;
  openFile: (fileName: string) => void;
  closeFile: (fileName: string) => void;
  updateFileContent: (fileName: string, content: string) => void;
  hydrateDemos: () => Promise<void>;

  // LSP Actions
  setLspStatus: (
    status: "disabled" | "connecting" | "connected" | "error"
  ) => void;
  setLspClient: (client: MonacoLanguageClient, worker: Worker) => void;
}

// Initial State Logic
const INITIAL_DEMO = DEMOS[0];
const initialFiles = INITIAL_DEMO.files.reduce((acc, file) => {
  acc[file.name] = file;
  return acc;
}, {} as Record<string, PlaygroundFile>);

export const usePlaygroundStore = create<PlaygroundState>((set, get) => ({
  files: initialFiles,
  openFiles: INITIAL_DEMO.files.slice(0, 3).map((f) => f.name),
  activeFileName: INITIAL_DEMO.activeFileName,

  lspStatus: "disabled",
  client: null,
  worker: null,

  setFiles: (files) => set({ files }),

  openFile: (fileName) =>
    set((state) => {
      if (!state.files[fileName]) return state; // File doesn't exist

      const newOpenFiles = state.openFiles.includes(fileName)
        ? state.openFiles
        : [...state.openFiles, fileName];

      return {
        openFiles: newOpenFiles,
        activeFileName: fileName,
      };
    }),

  closeFile: (fileName) =>
    set((state) => {
      const newOpenFiles = state.openFiles.filter((f) => f !== fileName);
      let newActive = state.activeFileName;

      if (state.activeFileName === fileName) {
        // If closing active file, switch to the last one or null
        newActive =
          newOpenFiles.length > 0
            ? newOpenFiles[newOpenFiles.length - 1]
            : null;
      }

      return {
        openFiles: newOpenFiles,
        activeFileName: newActive,
      };
    }),

  updateFileContent: (fileName, content) =>
    set((state) => ({
      files: {
        ...state.files,
        [fileName]: {
          ...state.files[fileName],
          content,
        },
      },
    })),

  hydrateDemos: async () => {
    const { files } = get();
    const updates: Record<string, PlaygroundFile> = {};
    let hasUpdates = false;

    for (const [name, file] of Object.entries(files)) {
      if (file.path && !file.content) {
        try {
          // Determine absolute URL or relative?
          // path is like /demo/laws.td (from public root)
          const response = await fetch(file.path);
          if (response.ok) {
            const text = await response.text();
            updates[name] = { ...file, content: text };
            hasUpdates = true;
          } else {
            console.error(`Failed to fetch demo file: ${file.path}`);
          }
        } catch (e) {
          console.error(`Error fetching demo file: ${file.path}`, e);
        }
      }
    }

    if (hasUpdates) {
      set((state) => ({
        files: { ...state.files, ...updates },
      }));
    }
  },

  setLspStatus: (status) => set({ lspStatus: status }),
  setLspClient: (client, worker) =>
    set({ client, worker, lspStatus: "connected" }),
}));
