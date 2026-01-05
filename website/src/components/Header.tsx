'use client'

import * as React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useTheme } from 'next-themes'
import { Moon, Sun, Github, Globe, ChevronDown, Menu, X } from 'lucide-react'
import { useParams, usePathname, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'

export function Header() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = React.useState(false)
  const [langOpen, setLangOpen] = React.useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false)
  const params = useParams()
  const pathname = usePathname()
  const router = useRouter()
  const lang = (params?.lang as string) || 'en'
  const langRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    setMounted(true)
    const handleClickOutside = (event: MouseEvent) => {
      if (langRef.current && !langRef.current.contains(event.target as Node)) {
        setLangOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close mobile menu when route changes
  React.useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  if (!mounted) {
    return (
      <nav className="sticky top-0 z-50 flex w-full justify-center border-b border-white/5 bg-background/80 backdrop-blur-xl">
        <div className="flex w-full max-w-7xl items-center justify-between px-6 py-4">
          <div className="h-8 w-[110px] animate-pulse rounded bg-gray-200 dark:bg-gray-800" />
          <div className="flex gap-4">
            <div className="h-9 w-9 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800" />
            <div className="h-9 w-9 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-800" />
          </div>
        </div>
      </nav>
    )
  }

  const isDark = theme === 'dark'
  const isZh = lang === 'zh'

  const getNewPathname = (newLang: string) => {
    // Simple replacement might be risky if URL structure is complex, 
    // but for /[lang]/... it should be fine as long as lang is the first segment.
    // A more robust way would be to split and replace the second segment.
    const segments = pathname.split('/')
    if (segments[1] === lang) {
        segments[1] = newLang
        return segments.join('/')
    }
    return pathname.replace(`/${lang}`, `/${newLang}`)
  }

  const languages = [
    { code: 'en', label: 'English', short: 'EN' },
    { code: 'zh', label: '简体中文', short: 'ZH' },
  ]

  const navLinks = [
    { href: `/${lang}/philosophy`, label: isZh ? '理念' : 'Philosophy' },
    { href: `/${lang}/docs`, label: isZh ? '文档' : 'Docs' },
    { href: `/${lang}/playground`, label: 'Playground', className: 'text-success font-semibold' },
  ]

  return (
    <nav className="sticky top-0 z-50 flex w-full justify-center border-b border-black/[0.03] dark:border-white/5 bg-background/80 backdrop-blur-xl shadow-[0_1px_2px_rgba(0,0,0,0.02)] dark:shadow-none">
      <div className="flex w-full max-w-7xl items-center justify-between px-6 py-4">
        <Link href={`/${lang}`} className="flex items-center gap-2 transition-opacity hover:opacity-80">
          <Image
            src={isDark ? "/logo-light.svg" : "/logo-dark.svg"}
            alt="Typedown Logo"
            width={110}
            height={32}
            priority
          />
        </Link>

        {/* Desktop Navigation */}
        <div className="flex items-center gap-6">
          <div className="hidden items-center gap-8 text-sm font-medium text-gray-500 sm:flex">
            {navLinks.map(link => (
              <Link 
                key={link.href} 
                href={link.href} 
                className={`hover:text-foreground transition-colors ${link.className || ''}`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="hidden sm:flex items-center gap-4 border-l border-black/10 dark:border-white/10 pl-6">
            <div className="relative" ref={langRef}>
              <button
                onClick={() => setLangOpen(!langOpen)}
                className="flex h-9 w-12 items-center justify-center gap-1 rounded-lg border border-black/10 dark:border-white/10 bg-transparent text-[11px] font-bold text-gray-500 transition-all duration-200 hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground active:scale-95"
                aria-label="Select language"
              >
                {lang.toUpperCase()}
                <ChevronDown size={10} className={`transition-transform duration-200 ${langOpen ? 'rotate-180' : ''}`} />
              </button>
              
              <AnimatePresence>
                {langOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.1 }}
                    className="absolute right-0 top-full mt-2 w-32 overflow-hidden rounded-xl border border-black/10 dark:border-white/10 bg-background/95 p-1 shadow-lg backdrop-blur-xl"
                  >
                    {languages.map((l) => (
                      <Link
                        key={l.code}
                        href={getNewPathname(l.code)}
                        className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors hover:bg-black/5 dark:hover:bg-white/5 ${
                          lang === l.code ? 'text-foreground bg-black/5 dark:bg-white/5' : 'text-gray-500'
                        }`}
                      >
                        {l.label}
                        {lang === l.code && <div className="h-1.5 w-1.5 rounded-full bg-success" />}
                      </Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <button
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/10 dark:border-white/10 bg-transparent text-gray-500 transition-all duration-200 hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground active:scale-90"
              aria-label="Toggle theme"
            >
              {mounted && (theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />)}
            </button>
            <a
              href="https://github.com/IndenScale/typedown"
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/10 dark:border-white/10 bg-transparent text-gray-500 transition-all duration-200 hover:bg-black/5 dark:hover:bg-white/5 hover:text-foreground active:scale-90"
              aria-label="GitHub Repository"
            >
              <Github size={18} />
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="sm:hidden flex items-center justify-center w-9 h-9 rounded-lg hover:bg-black/5 dark:hover:bg-white/5"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="absolute top-full left-0 w-full bg-background border-b border-black/5 dark:border-white/5 sm:hidden overflow-hidden"
          >
             <div className="px-6 py-4 flex flex-col gap-4">
                {navLinks.map(link => (
                  <Link 
                    key={link.href} 
                    href={link.href} 
                    className={`text-base font-medium py-2 ${link.className || 'text-gray-500'}`}
                  >
                    {link.label}
                  </Link>
                ))}
                
                <div className="h-px w-full bg-black/5 dark:bg-white/5 my-2" />
                
                <div className="flex flex-col gap-2">
                    <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">Language</span>
                    <div className="flex gap-2">
                        {languages.map(l => (
                            <Link
                                key={l.code}
                                href={getNewPathname(l.code)}
                                className={`px-3 py-1.5 rounded-md text-sm font-medium border ${
                                    lang === l.code 
                                    ? 'border-success/20 bg-success/5 text-success' 
                                    : 'border-black/10 dark:border-white/10 text-gray-500'
                                }`}
                            >
                                {l.short}
                            </Link>
                        ))}
                    </div>
                </div>
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}

