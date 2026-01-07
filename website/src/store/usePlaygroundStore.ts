import { create } from "zustand";
import { debounce } from "lodash";
import type { MonacoLanguageClient } from "monaco-languageclient";
import type { Diagnostic } from "vscode-languageserver-protocol";
import { getDemos } from "@/lib/demos";

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
  diagnostics: Record<string, Diagnostic[]>;

  // Demo State
  currentDemoId: string;
  lang: string;

  // Actions
  setFiles: (files: Record<string, PlaygroundFile>) => void;
  openFile: (fileName: string) => void;
  closeFile: (fileName: string) => void;
  updateFileContent: (fileName: string, content: string) => void;
  hydrateDemos: () => Promise<void>;
  selectDemo: (demoId: string) => Promise<void>;
  setLang: (lang: string) => void;

  // LSP Actions
  setLspStatus: (
    status: "disabled" | "connecting" | "connected" | "error"
  ) => void;
  setLspClient: (client: MonacoLanguageClient, worker: Worker) => void;
  setDiagnostics: (uri: string, diagnostics: Diagnostic[]) => void;
}

// Initial State Logic (default to 'en')
const DEFAULT_LANG = "en";
const INITIAL_DEMOS = getDemos(DEFAULT_LANG);
const INITIAL_DEMO = INITIAL_DEMOS[0];
const initialFiles = INITIAL_DEMO.files.reduce((acc, file) => {
  acc[file.name] = {
    ...file,
    content: file.content || "",
    language: file.language as string,
  };
  return acc;
}, {} as Record<string, PlaygroundFile>);

const debouncedLspUpdate = debounce(
  (client: MonacoLanguageClient, uri: string, content: string) => {
    client.sendNotification("typedown/updateFile", { uri, content });
  },
  200
); // 200ms Transmission Debounce

export const usePlaygroundStore = create<PlaygroundState>((set, get) => ({
  files: initialFiles,
  openFiles: INITIAL_DEMO.files.slice(0, 3).map((f) => f.name),
  activeFileName: INITIAL_DEMO.activeFileName,
  currentDemoId: INITIAL_DEMO.id,
  lang: DEFAULT_LANG,

  lspStatus: "disabled",
  client: null,
  worker: null,
  diagnostics: {},

  setFiles: (files) => set({ files }),

  setLang: (lang) => {
    const currentLang = get().lang;
    if (currentLang === lang) return;

    set({ lang });

    // Force re-select current demo to update localized content/paths
    const currentDemoId = get().currentDemoId;
    get().selectDemo(currentDemoId);
  },

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

  updateFileContent: (fileName, content) => {
    set((state) => ({
      files: {
        ...state.files,
        [fileName]: {
          ...state.files[fileName],
          content,
        },
      },
    }));

    // Manual Sync with Debounce
    const { client, files } = get();
    if (client) {
      const file = files[fileName];
      // Ensure we use the latest content from the fn arg, as state might not update instantly in closure?
      // Actually set() is synchronous for the store, but good to be safe.
      // Also stick to the URI convention:
      const logicalPath = file.path || `/${file.name}`;
      const uri = `file://${logicalPath}`;

      debouncedLspUpdate(client, uri, content);
    }
  },

  selectDemo: async (demoId) => {
    const lang = get().lang;
    const demos = getDemos(lang);
    const demo = demos.find((d) => d.id === demoId);
    if (!demo) return;

    const newFiles = demo.files.reduce((acc, file) => {
      acc[file.name] = {
        ...file,
        content: file.content || "",
        language: file.language as string,
      };
      return acc;
    }, {} as Record<string, PlaygroundFile>);

    set({
      currentDemoId: demoId,
      files: newFiles,
      openFiles: demo.files.slice(0, 3).map((f) => f.name),
      activeFileName: demo.activeFileName,
    });

    // Trigger hydration for new files
    // Await hydration to ensure content is ready
    await get().hydrateDemos();

    // Trigger full validation (LSP)
    // We add a delay to ensure Monaco has processed the file switches (didOpen)
    // and the worker has synced the new content.
    const client = get().client;
    if (client) {
      // Use get().files to ensure we have the hydrated content
      const currentFiles = get().files;

      // 1. Prepare Bulk Payload
      const filesPayload: Array<{ uri: string; content: string }> = [];

      Object.values(currentFiles).forEach((file) => {
        // Use the full logical path to match LSP's view
        // Ensure we use the exact same logic as the Editor for consistency
        const logicalPath = file.path || `/${file.name}`;
        const uri = `file://${logicalPath}`;
        filesPayload.push({
          uri,
          content: file.content || "",
        });
      });

      console.log(
        "[Playground] Hydrating project with files:",
        filesPayload.map((f) => f.uri)
      );

      // 2. Send Bulk Load Notification
      // This will Populate Overlay -> Scan -> Parse -> Compile -> Publish Diagnostics
      client.sendNotification("typedown/loadProject", {
        files: filesPayload,
      });
    }
  },

  hydrateDemos: async () => {
    const { files } = get();
    const updates: Record<string, PlaygroundFile> = {};
    let hasUpdates = false;

    for (const [name, file] of Object.entries(files)) {
      if (file.path && !file.content) {
        try {
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
  setDiagnostics: (uri, diagnostics) =>
    set((state) => ({
      diagnostics: {
        ...state.diagnostics,
        [uri]: diagnostics,
      },
    })),
}));
