import { createHighlighter, type Highlighter } from 'shiki'
import typedownGrammar from './typedown.tmLanguage.json'

let highlighterInstance: Highlighter | null = null

export async function getHighlighter() {
  if (highlighterInstance) return highlighterInstance

  highlighterInstance = await createHighlighter({
    themes: ['github-dark', 'github-light'],
    langs: [
      'python',
      'markdown',
      'yaml',
      {
        ...(typedownGrammar as any),
        name: 'typedown',
      }
    ],
  })
  return highlighterInstance
}

export async function highlight(code: string, lang: string = 'typedown', theme: string = 'github-dark') {
  const highlighter = await getHighlighter()
  
  // Ensure the language is loaded even if it's dynamic
  if (!highlighter.getLoadedLanguages().includes(lang)) {
    if (lang === 'typedown') {
      await highlighter.loadLanguage({
        ...(typedownGrammar as any),
        name: 'typedown',
      })
    } else {
      await highlighter.loadLanguage(lang as any)
    }
  }

  return highlighter.codeToHtml(code, {
    lang,
    theme,
  })
}
