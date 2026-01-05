'use client'

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, FileCode } from 'lucide-react'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { highlight } from '@/lib/shiki'

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

interface CodeEditorProps {
  fileName: string
  code: string
  errorLine?: number
  errorMessage?: string
  className?: string
}

export function CodeEditor({
  fileName,
  code,
  errorLine,
  errorMessage,
  className,
}: CodeEditorProps) {
  const [highlightedHtml, setHighlightedHtml] = useState<string[]>([])
  const lines = code.split('\n')

  useEffect(() => {
    async function doHighlight() {
      const htmls = await Promise.all(
        lines.map(line => highlight(line || ' ', 'typedown'))
      )
      setHighlightedHtml(htmls)
    }
    doHighlight()
  }, [code])

  return (
    <div className={cn("w-full overflow-hidden rounded-xl border border-white/10 bg-[#0A0A0A] shadow-2xl", className)}>
      {/* Tab Header */}
      <div className="flex items-center gap-2 border-b border-white/5 bg-white/5 px-4 py-3">
        <div className="flex gap-1.5">
          <div className="h-3 w-3 rounded-full bg-[#FF5F56]/20" />
          <div className="h-3 w-3 rounded-full bg-[#FFBD2E]/20" />
          <div className="h-3 w-3 rounded-full bg-[#27C93F]/20" />
        </div>
        <div className="ml-4 flex items-center gap-2 text-xs font-mono text-gray-400">
          <FileCode size={14} className="text-success/60" />
          {fileName}
        </div>
      </div>

      {/* Editor Content */}
      <div className="relative flex p-6 text-left font-mono text-sm leading-relaxed sm:text-base overflow-x-auto">
        {/* Line Numbers */}
        <div className="mr-6 flex flex-col text-gray-700 select-none text-right min-w-[2rem]">
          {lines.map((_, i) => (
            <span key={i} className={cn(errorLine === i + 1 && "text-error/40 font-bold")}>
              {i + 1}
            </span>
          ))}
        </div>

        {/* Code Area */}
        <div className="flex-1 relative">
          {lines.map((line, i) => {
            const isErrorLine = errorLine === i + 1
            const html = highlightedHtml[i]

            return (
              <div key={i} className="group relative min-h-[1.5rem]">
                <span className={cn(
                  "relative z-10 block",
                  isErrorLine && "red-wave"
                )}>
                  {html ? (
                    <span 
                      dangerouslySetInnerHTML={{ __html: html.replace(/<pre[^>]*>|<\/pre>|<code>|<\/code>/g, '') }} 
                      className="[&>span]:bg-transparent!"
                    />
                  ) : (
                    <span className="text-gray-300">{line}</span>
                  )}
                </span>

                {/* Error Tooltip */}
                <AnimatePresence>
                  {isErrorLine && errorMessage && (
                    <motion.div
                      initial={{ opacity: 0, y: 5, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      className="mt-2 relative z-20 inline-flex items-start gap-3 rounded-lg border border-error/20 bg-error/10 p-4 text-xs text-error shadow-2xl backdrop-blur-md max-w-sm"
                    >
                      <AlertCircle size={16} className="mt-0.5 shrink-0" />
                      <div className="space-y-1">
                        <p className="font-semibold leading-none">Typedown Validation Error</p>
                        <p className="text-error/80 leading-relaxed">{errorMessage}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
