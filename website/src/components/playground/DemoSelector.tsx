'use client'

import { usePlayground } from './PlaygroundContext'
import { DEMOS } from '@/lib/demos'
import { ChevronDown } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

export function DemoSelector() {
  const { currentDemoId, selectDemo } = usePlayground()
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const currentDemo = DEMOS.find(d => d.id === currentDemoId)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-colors border border-transparent hover:border-black/10 dark:hover:border-white/10"
      >
        <span className="text-gray-500">Demo:</span>
        <span className="text-foreground">{currentDemo?.name}</span>
        <ChevronDown size={14} className="text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-64 p-1 bg-white dark:bg-[#111] rounded-lg shadow-xl border border-black/10 dark:border-white/10 z-50">
          {DEMOS.map((demo) => (
            <button
              key={demo.id}
              onClick={() => {
                selectDemo(demo.id)
                setIsOpen(false)
              }}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                currentDemoId === demo.id
                  ? 'bg-success/10 text-success'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground'
              }`}
            >
              <div className="font-medium">{demo.name}</div>
              <div className="text-xs opacity-70 truncate">{demo.description}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
