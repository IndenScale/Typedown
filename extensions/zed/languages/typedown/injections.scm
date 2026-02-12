; Language injections for Typedown code blocks
; This enables syntax highlighting inside fenced code blocks

; Python code in model blocks
(fenced_code_block
  (info_string
    (language) @_lang)
  (code_fence_content) @injection.content
  (#match? @_lang "^model$")
  (#set! injection.language "python"))

; Python code in spec blocks
(fenced_code_block
  (info_string
    (language) @_lang)
  (code_fence_content) @injection.content
  (#match? @_lang "^spec$")
  (#set! injection.language "python"))

; Python code in config:python blocks
(fenced_code_block
  (info_string
    (language) @_lang)
  (code_fence_content) @injection.content
  (#match? @_lang "^config$")
  (#set! injection.language "python"))

; YAML code in entity blocks
(fenced_code_block
  (info_string
    (language) @_lang)
  (code_fence_content) @injection.content
  (#match? @_lang "^entity$")
  (#set! injection.language "yaml"))

; Standard language injections (from info string)
(fenced_code_block
  (info_string
    (language) @injection.language)
  (code_fence_content) @injection.content)

; Inline code
((inline) @injection.content
  (#set! injection.language "typedown-inline"))
