"use client";

import React, { createContext, useContext, useReducer } from "react";
import { DEMOS, Demo, File } from "@/lib/demos";

// --- State Types ---

interface PlaygroundState {
  currentDemoId: string;
  files: File[];
  activeFileName: string;
  openFiles: string[]; // List of filenames currently open in tabs
}

type Action =
  | { type: "SELECT_DEMO"; payload: string }
  | { type: "SELECT_FILE"; payload: string }
  | { type: "CLOSE_FILE"; payload: string }
  | {
      type: "UPDATE_FILE_CONTENT";
      payload: { fileName: string; content: string };
    }
  | { type: "RESET_FILE"; payload: { fileName: string } };

// --- Initial State ---

const INITIAL_DEMO = DEMOS[0];
const initialState: PlaygroundState = {
  currentDemoId: INITIAL_DEMO.id,
  files: INITIAL_DEMO.files,
  activeFileName: INITIAL_DEMO.activeFileName,
  openFiles: INITIAL_DEMO.files.slice(0, 3).map((f) => f.name),
};

// --- Reducer ---

function playgroundReducer(
  state: PlaygroundState,
  action: Action
): PlaygroundState {
  switch (action.type) {
    case "SELECT_DEMO": {
      const demo = DEMOS.find((d) => d.id === action.payload);
      if (!demo) return state;
      return {
        currentDemoId: demo.id,
        files: demo.files, // Reset files to demo defaults
        activeFileName: demo.activeFileName,
        openFiles: demo.files.slice(0, 3).map((f) => f.name),
      };
    }
    case "SELECT_FILE": {
      const isOpen = state.openFiles.includes(action.payload);
      return {
        ...state,
        activeFileName: action.payload,
        openFiles: isOpen
          ? state.openFiles
          : [...state.openFiles, action.payload],
      };
    }
    case "CLOSE_FILE": {
      const fileToClose = action.payload;
      const newOpenFiles = state.openFiles.filter((f) => f !== fileToClose);

      let newActiveFileName = state.activeFileName;
      // If we closed the active file, switch to the one to its left, or the first one
      if (state.activeFileName === fileToClose) {
        if (newOpenFiles.length > 0) {
          const closedIndex = state.openFiles.indexOf(fileToClose);
          // Try to go to the left (index - 1), otherwise go to the new file at that index (which is the one to the right), or the last one
          const newIndex = Math.max(0, closedIndex - 1);
          // Ensure index is within bounds of NEW array
          const safeIndex = Math.min(newIndex, newOpenFiles.length - 1);
          newActiveFileName = newOpenFiles[safeIndex];
        } else {
          // No files open? Might want to handle this case, or keep it empty.
          // For now, let's keep it empty or maybe prevent closing last tab?
          // Implementation choice: allow closing all, active becomes empty string?
          // The Editor component should handle "No file selected"
          newActiveFileName = "";
        }
      }

      return {
        ...state,
        openFiles: newOpenFiles,
        activeFileName: newActiveFileName,
      };
    }
    case "UPDATE_FILE_CONTENT": {
      return {
        ...state,
        files: state.files.map((f) =>
          f.name === action.payload.fileName
            ? { ...f, content: action.payload.content }
            : f
        ),
      };
    }
    case "RESET_FILE": {
      // Find original content from DEMOS
      const originalDemo = DEMOS.find((d) => d.id === state.currentDemoId);
      const originalFile = originalDemo?.files.find(
        (f) => f.name === action.payload.fileName
      );

      if (!originalFile) return state;

      return {
        ...state,
        files: state.files.map((f) =>
          f.name === action.payload.fileName
            ? { ...f, content: originalFile.content }
            : f
        ),
      };
    }
    default:
      return state;
  }
}

// --- Context ---

interface PlaygroundContextType extends PlaygroundState {
  currentDemo: Demo;
  activeFile: File | undefined;
  selectDemo: (id: string) => void;
  selectFile: (fileName: string) => void;
  closeFile: (fileName: string) => void;
  updateFileContent: (fileName: string, content: string) => void;
  resetFile: (fileName: string) => void;
}

const PlaygroundContext = createContext<PlaygroundContextType | null>(null);

export function PlaygroundProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [state, dispatch] = useReducer(playgroundReducer, initialState);

  // Derived state
  const currentDemo =
    DEMOS.find((d) => d.id === state.currentDemoId) || DEMOS[0];
  const activeFile = state.files.find((f) => f.name === state.activeFileName);

  const value: PlaygroundContextType = {
    ...state,
    currentDemo,
    activeFile,
    selectDemo: (id) => dispatch({ type: "SELECT_DEMO", payload: id }),
    selectFile: (fileName) =>
      dispatch({ type: "SELECT_FILE", payload: fileName }),
    closeFile: (fileName) =>
      dispatch({ type: "CLOSE_FILE", payload: fileName }),
    updateFileContent: (fileName, content) =>
      dispatch({ type: "UPDATE_FILE_CONTENT", payload: { fileName, content } }),
    resetFile: (fileName) =>
      dispatch({ type: "RESET_FILE", payload: { fileName } }),
  };

  return (
    <PlaygroundContext.Provider value={value}>
      {children}
    </PlaygroundContext.Provider>
  );
}

// --- Hook ---

export function usePlayground() {
  const context = useContext(PlaygroundContext);
  if (!context) {
    throw new Error("usePlayground must be used within a PlaygroundProvider");
  }
  return context;
}
