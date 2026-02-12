; Indentation rules for Typedown
; Inherits from Markdown behavior

; Indent inside fenced code blocks
(fenced_code_block) @indent

; Indent inside list items
(list_item) @indent

; Indent inside block quotes
(block_quote) @indent

; Auto-dedent at end of code blocks
(fenced_code_block
  (code_fence_content) @end)
