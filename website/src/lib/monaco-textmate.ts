import { loadWASM } from 'vscode-oniguruma'
import { Registry } from 'monaco-textmate'
import { wireTmGrammars } from 'monaco-editor-textmate'
import type { Monaco } from '@monaco-editor/react'

let wasmLoaded = false

export async function setupMonacoTextMate(monaco: Monaco, editor: any) {
  if (!wasmLoaded) {
    const response = await fetch('/onig.wasm')
    const data = await response.arrayBuffer()
    await loadWASM(data)
    wasmLoaded = true
  }

  const registry = new Registry({
    getGrammarDefinition: async (scopeName) => {
      let path = ''
      if (scopeName === 'source.typedown') path = '/grammars/typedown.tmLanguage.json'
      else if (scopeName === 'source.python') path = '/grammars/python.tmLanguage.json'
      else if (scopeName === 'text.html.markdown') path = '/grammars/markdown.tmLanguage.json'
      
      if (!path) {
        throw new Error(`Unknown scope name: ${scopeName}`)
      }

      const content = await (await fetch(path)).json()
      return {
        format: 'json',
        content,
      }
    },
  })

  // Map language IDs to their root scope names
  const grammars = new Map()
  grammars.set('typedown', 'source.typedown')
  grammars.set('python', 'source.python')
  
  await wireTmGrammars(monaco, registry, grammars, editor)
}
