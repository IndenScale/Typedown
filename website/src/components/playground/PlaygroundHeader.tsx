'use client'

import { DemoSelector } from './DemoSelector'
import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'


export function PlaygroundHeader() {
  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-black/5 dark:border-white/5 bg-white dark:bg-[#0A0A0A]">
      <div className="flex items-center gap-4">
        <Link 
          href="/"
          className="p-2 text-gray-500 hover:text-foreground transition-colors rounded-md hover:bg-black/5 dark:hover:bg-white/5"
        >
          <ArrowLeft size={18} />
        </Link>
        <div className="font-bold text-lg tracking-tight">
          Typedown <span className="text-xs font-mono font-normal text-success bg-success/10 px-1.5 py-0.5 rounded ml-1">PLAYGROUND</span>
        </div>
      </div>

      <DemoSelector />

      <div className="flex items-center gap-2">
        {/* Placeholder for future actions like "Run" or "Export" */}
        <div className="text-xs text-gray-400">
          v0.2.12
        </div>
      </div>
    </header>
  )
}
