; Bracket matching for Typedown
; Extends Markdown brackets with Typedown-specific patterns

; Standard Markdown brackets
("[" @open "]" @close)
("(" @open ")" @close)
("{" @open "}" @close)
("<" @open ">" @close)

; Typedown wiki link brackets: [[ ... ]]
((link_text) @wiki_link
  (#match? @wiki_link "^\\[\\[")
  (#set! rainbow.include))

; Code block markers
("```" @open "```" @close)
