'use client'

import { useEffect, useRef, useState } from 'react'
import Editor, { useMonaco, type Monaco } from '@monaco-editor/react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { FileCode } from 'lucide-react'
import { useTheme } from 'next-themes'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

interface RealCodeEditorProps {
  fileName: string
  code: string
  markers?: {
    startLineNumber: number
    startColumn: number
    endLineNumber: number
    endColumn: number
    message: string
    severity: number // 8 is MarkerSeverity.Error
  }[]
  className?: string
  height?: string
  autoHeight?: boolean
}

export function RealCodeEditor({
  fileName,
  code,
  markers = [],
  className,
  height = "400px",
  autoHeight = false,
}: RealCodeEditorProps) {
  const monaco = useMonaco()
  const editorRef = useRef<any>(null)
  const { resolvedTheme } = useTheme()
  const [mounted, setMounted] = useState(false)
  const [editorHeight, setEditorHeight] = useState(height)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!autoHeight) {
      setEditorHeight(height)
    }
  }, [height, autoHeight])

  function handleBeforeMount(monaco: Monaco) {
    // Register Typedown language
    monaco.languages.register({ id: 'typedown' })

    monaco.languages.setMonarchTokensProvider('typedown', {
      tokenizer: {
        root: [
          [/^#\s.*$/, 'keyword.directive'], // Headers
          [/^```\w+.*$/, 'string.link'], // Code block start
          [/^```$/, 'string.link'], // Code block end
          [/entity\s+[A-Z][\w]*:/, 'keyword'], // Entity declaration
          [/[a-z_][\w]*:/, 'type.identifier'], // Keys
          [/"[^"]*"/, 'string'],
          [/\d+/, 'number'],
          [/#.*$/, 'comment'],
          [/\[\[.*?\]\]/, 'string.link'], // Wiki-links
          // Python-like keywords for inside blocks (simplified)
          [/\b(class|def|if|else|return|raise|import|from|pass)\b/, 'keyword'],
          [/\b(BaseModel)\b/, 'type.identifier'],
        ],
      },
    })

    // Define Dark Theme
    monaco.editor.defineTheme('typedown-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: 'ff5f56', fontStyle: 'bold' },
        { token: 'keyword.directive', foreground: 'ffffff', fontStyle: 'bold' },
        { token: 'type.identifier', foreground: '27c93f' },
        { token: 'string', foreground: 'ffbd2e' },
        { token: 'string.link', foreground: '569cd6', fontStyle: 'underline' },
        { token: 'comment', foreground: '6a737d' },
      ],
      colors: {
        'editor.background': '#0A0A0A',
        'editor.lineHighlightBackground': '#FFFFFF05',
      },
    })

    // Define Light Theme
    monaco.editor.defineTheme('typedown-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'keyword', foreground: 'd73a49', fontStyle: 'bold' },
        { token: 'keyword.directive', foreground: '24292e', fontStyle: 'bold' },
        { token: 'type.identifier', foreground: '22863a' },
        { token: 'string', foreground: '032f62' },
        { token: 'string.link', foreground: '005cc5', fontStyle: 'underline' },
        { token: 'comment', foreground: '6a737d' },
      ],
      colors: {
        'editor.background': '#FFFFFF',
        'editor.lineHighlightBackground': '#00000005',
      },
    })
  }

  useEffect(() => {
    if (editorRef.current && monaco && markers.length > 0) {
      monaco.editor.setModelMarkers(
        editorRef.current.getModel(),
        'owner',
        markers
      )
    }
  }, [monaco, markers])

  function handleEditorDidMount(editor: any) {
    editorRef.current = editor
    
    // Disable scrolling beyond last line
    editor.updateOptions({
      scrollBeyondLastLine: false,
      minimap: { enabled: false },
      overviewRulerLanes: 0,
      hideCursorInOverviewRuler: true,
      scrollbar: {
        vertical: 'hidden',
        horizontal: 'hidden',
      },
      fontFamily: 'Menlo, Monaco, "Courier New", monospace',
      fontSize: 14,
      lineHeight: 24,
      renderLineHighlight: 'all',
      contextmenu: false,
      scrollBeyondLastColumn: 0,
    })

    if (autoHeight) {
      const updateHeight = () => {
        const contentHeight = editor.getContentHeight()
        setEditorHeight(`${contentHeight}px`)
        editor.layout({ width: editor.getLayoutInfo().width, height: contentHeight })
      }
      editor.onDidContentSizeChange(updateHeight)
      updateHeight()
    }
  }

  const editorTheme = mounted && resolvedTheme === 'dark' ? 'typedown-dark' : 'typedown-light'

  return (
    <div className={cn(
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
          <FileCode size={14} className="text-success/80 dark:text-success/60" />
          {fileName}
        </div>
      </div>

      {/* Editor Content */}
      <div style={{ height: editorHeight }} className="transition-[height] duration-200 ease-out">
        <Editor
          height="100%"
          defaultLanguage="typedown"
          defaultValue={code}
          theme={editorTheme}
          beforeMount={handleBeforeMount}
          onMount={handleEditorDidMount}
          options={{
            readOnly: false,
            wordWrap: 'on',
            scrollBeyondLastLine: false,
          }}
        />
      </div>
    </div>
  )
}
