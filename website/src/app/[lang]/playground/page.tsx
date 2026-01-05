'use client'

import { PlaygroundProvider } from '@/components/playground/PlaygroundContext'
import { PlaygroundHeader } from '@/components/playground/PlaygroundHeader'
import { FileExplorer } from '@/components/playground/FileExplorer'
import { PlaygroundEditor } from '@/components/playground/PlaygroundEditor'

export default function PlaygroundPage() {
  return (
    <PlaygroundProvider>
      <div className="flex h-screen w-full flex-col bg-background text-foreground overflow-hidden">
        <PlaygroundHeader />
        
        <div className="flex flex-1 overflow-hidden">
          <FileExplorer />
          
          <main className="flex-1 relative bg-white dark:bg-[#0A0A0A]">
             <PlaygroundEditor />
          </main>
        </div>
      </div>
    </PlaygroundProvider>
  )
}
