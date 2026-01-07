"use client";

import { useEffect, useRef, useState } from "react";
import Editor, { useMonaco, type Monaco } from "@monaco-editor/react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { FileCode } from "lucide-react";
import { useTheme } from "next-themes";
import {
  TYPEDOWN_THEME_DARK,
  TYPEDOWN_THEME_LIGHT,
} from "@/lib/typedown-theme";
import { textmateService } from "@/services/MonacoTextmateService";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface PlaygroundEditorProps {
  fileName: string;
  code: string;
  markers?: {
    startLineNumber: number;
    startColumn: number;
    endLineNumber: number;
    endColumn: number;
    message: string;
    severity: number; // 8 is MarkerSeverity.Error
  }[];
  className?: string;
  height?: string;
  autoHeight?: boolean;
}

export function LandingCodeEditor({
  fileName,
  code,
  markers = [],
  className,
  height = "400px",
  autoHeight = false,
}: PlaygroundEditorProps) {
  const monaco = useMonaco();
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const editorRef = useRef<any>(null);
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  // Store content height specifically for auto-height mode
  const [contentHeight, setContentHeight] = useState<string | null>(null);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setMounted(true);
  }, []);

  function handleBeforeMount(monaco: Monaco) {
    // Register Typedown language
    if (
      !monaco.languages
        .getLanguages()
        .some((l: { id: string }) => l.id === "typedown")
    ) {
      monaco.languages.register({ id: "typedown" });
    }

    // Define Dark Theme
    monaco.editor.defineTheme("typedown-dark", TYPEDOWN_THEME_DARK);

    // Define Light Theme
    monaco.editor.defineTheme("typedown-light", TYPEDOWN_THEME_LIGHT);
  }

  // Handle markers updates (e.g. if props change after mount)
  useEffect(() => {
    if (editorRef.current && monaco && markers.length > 0) {
      monaco.editor.setModelMarkers(
        editorRef.current.getModel(),
        "typedown",
        markers
      );
    }
  }, [monaco, markers]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async function handleEditorDidMount(editor: any, monaco: Monaco) {
    editorRef.current = editor;

    // Wire TextMate grammar
    await textmateService.wire(monaco);
    
    // Force refresh to apply TextMate highlighting
    const model = editor.getModel();
    if (model) {
      monaco.editor.setModelLanguage(model, "typedown");
    }

    // Set initial markers immediately
    if (markers.length > 0) {
      monaco.editor.setModelMarkers(editor.getModel(), "typedown", markers);
    }

    // Disable scrolling beyond last line
    editor.updateOptions({
      scrollBeyondLastLine: false,
      minimap: { enabled: false },
      overviewRulerLanes: 0,
      hideCursorInOverviewRuler: true,
      scrollbar: {
        vertical: "hidden",
        horizontal: "hidden",
      },
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      fontSize: 14,
      lineHeight: 24,
      renderLineHighlight: "all",
      contextmenu: false,
      scrollBeyondLastColumn: 0,
    });

    if (autoHeight) {
      const updateHeight = () => {
        const h = editor.getContentHeight();
        setContentHeight(`${h}px`);
        editor.layout({
          width: editor.getLayoutInfo().width,
          height: h,
        });
      };
      editor.onDidContentSizeChange(updateHeight);
      updateHeight();
    }
  }

  const editorTheme =
    mounted && resolvedTheme === "dark" ? "typedown-dark" : "typedown-light";

  // Derive final height: if autoHeight is on and we have a contentHeight, use it.
  // Otherwise, fallback to the fixed height prop.
  const finalHeight = autoHeight && contentHeight ? contentHeight : height;

  return (
    <div
      className={cn(
        "w-full overflow-hidden rounded-xl border shadow-2xl transition-all duration-200",
        "border-black/10 bg-white text-black",
        "dark:border-white/10 dark:bg-[#0A0A0A] dark:text-white",
        className
      )}>
      {/* Tab Header */}
      <div className="flex items-center gap-2 border-b border-black/5 bg-black/5 dark:border-white/5 dark:bg-white/5 px-4 py-3">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#FF5F56]/20" />
          <div className="h-3 w-3 rounded-full bg-[#FFBD2E]/20" />
          <div className="h-3 w-3 rounded-full bg-[#27C93F]/20" />
        </div>
        <div className="ml-4 flex items-center gap-2 text-xs font-mono text-gray-500 dark:text-gray-400">
          <FileCode
            size={14}
            className="text-success/80 dark:text-success/60"
          />
          {fileName}
        </div>
      </div>

      {/* Editor Content */}
      <div
        style={{ height: finalHeight }}
        className="transition-[height] duration-200 ease-out">
        <Editor
          height="100%"
          defaultLanguage="typedown"
          defaultValue={code}
          theme={editorTheme}
          beforeMount={handleBeforeMount}
          onMount={handleEditorDidMount}
          options={{
            readOnly: false,
            wordWrap: "on",
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  );
}
