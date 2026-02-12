; inherits: markdown

; Typedown-specific syntax highlighting
; This extends the base Markdown highlights

; Wiki Links: [[entity-id]]
((link_text) @link_text
  (#match? @link_text "^\\[\\["))

; Fenced code blocks with Typedown directives
(fenced_code_block
  (info_string
    (language) @keyword.directive)
  (#match? @keyword.directive "^(model|entity|spec|config)$"))

; Model block: ```model:ModelName
(fenced_code_block
  (info_string
    (language) @keyword.directive
    ") @entity.name.class
  (#match? @keyword.directive "^model$"))

; Entity block: ```entity Type: entity-id
(fenced_code_block
  (info_string
    (language) @keyword.directive)
  (#match? @keyword.directive "^entity$"))

; Spec block: ```spec:spec_name
(fenced_code_block
  (info_string
    (language) @keyword.directive)
  (#match? @keyword.directive "^spec$"))

; Config block: ```config:python
(fenced_code_block
  (info_string
    (language) @keyword.directive)
  (#match? @keyword.directive "^config$"))

; Highlight the [[ and ]] brackets in wiki links
([
  "[["
  "]]"
] @punctuation.bracket)

; Make wiki link text stand out
(
  (link_text) @string.special.symbol
  (#match? @string.special.symbol "^\\[\\[.+\\]\\]$"))
