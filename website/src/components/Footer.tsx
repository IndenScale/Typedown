'use client'

import * as React from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useTheme } from 'next-themes'
import { useParams } from 'next/navigation'

export function Footer() {
  const { theme } = useTheme()
  const [mounted, setMounted] = React.useState(false)
  const params = useParams()
  const lang = (params?.lang as string) || 'en'

  React.useEffect(() => {
    setMounted(true)
  }, [])

  const isDark = mounted && theme === 'dark'
  const isZh = lang === 'zh'

  const content = {
    tagline: isZh 
      ? "Markdown 的自由，代码级的严谨。"
      : "Markdown that catches errors. Before your team does.",
    subTagline: isZh
      ? "面向 AI 协作的知识建模语言。"
      : "The future of collaborative knowledge engineering.",
    product: isZh ? "产品" : "Product",
    company: isZh ? "关于" : "Company",
    docs: isZh ? "文档" : "Documentation",
    manifesto: isZh ? "宣言" : "Manifesto",
    contact: isZh ? "联系我们" : "Contact",
    copyright: isZh 
      ? `© ${new Date().getFullYear()} Monoco. 为精英开发者与 AI Agent 打造。`
      : `© ${new Date().getFullYear()} Monoco. Built for Elite Developers and AI Agents.`
  }

  return (
    <footer className="w-full border-t border-black/[0.03] dark:border-white/5 bg-background py-16 shadow-[0_-1px_2px_rgba(0,0,0,0.01)] dark:shadow-none">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid grid-cols-2 gap-12 sm:grid-cols-6">
          <div className="col-span-1 sm:col-span-2">
            <Link href={`/${lang}`} className="inline-block">
              {mounted ? (
                <Image
                  src={isDark ? "/logo-light.svg" : "/logo-dark.svg"}
                  alt="Typedown Logo"
                  width={100}
                  height={30}
                  className="opacity-80"
                />
              ) : (
                <div className="h-8 w-[100px] animate-pulse rounded bg-gray-200 dark:bg-gray-800" />
              )}
            </Link>
            <p className="mt-4 max-w-xs text-sm text-gray-500 leading-relaxed">
              {content.tagline}
              <br />
              {content.subTagline}
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{content.product}</h3>
            <ul className="mt-4 space-y-3 text-sm text-gray-500">
              <li>
                <Link href={`/${lang}/docs`} className="hover:text-foreground transition-colors">{content.docs}</Link>
              </li>
              <li>
                <a 
                  href="https://marketplace.visualstudio.com/items?itemName=Typedown.typedown-vscode-integration" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="hover:text-foreground transition-colors"
                >
                  VS Code Extension
                </a>
              </li>
              <li>
                <a 
                  href="https://open-vsx.org/extension/Typedown/typedown-vscode-integration" 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="hover:text-foreground transition-colors"
                >
                  Open VSX Registry
                </a>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">CLI Tool</Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{content.company}</h3>
            <ul className="mt-4 space-y-3 text-sm text-gray-500">
              <li>
                <Link href={`/${lang}/philosophy/manifesto`} className="hover:text-foreground transition-colors">{content.manifesto}</Link>
              </li>
              <li>
                <Link href="https://github.com/IndenScale/typedown" className="hover:text-foreground transition-colors">GitHub</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">{content.contact}</Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 border-t border-white/5 pt-8 text-center sm:text-left">
          <p className="text-xs text-gray-500">
            {content.copyright}
          </p>
        </div>
      </div>
    </footer>
  )
}
