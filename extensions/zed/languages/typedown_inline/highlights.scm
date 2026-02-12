; Typedown syntax highlighting - Extended from Markdown

; Code spans and link titles
[
  (code_span)
  (link_title)
] @text.literal

; Delimiters
[
  (emphasis_delimiter)
  (code_span_delimiter)
] @punctuation.delimiter

; Emphasis
(emphasis) @text.emphasis

; Strong emphasis
(strong_emphasis) @text.strong

; Links and URIs
[
  (link_destination)
  (uri_autolink)
] @text.uri

; Link text and references
[
  (link_label)
  (link_text)
  (image_description)
] @text.reference

; Escape sequences
[
  (backslash_escape)
  (hard_line_break)
] @string.escape

; Images
(image
  [
    "!"
    "["
    "]"
    "("
    ")"
  ] @punctuation.delimiter)

; Inline links
(inline_link
  [
    "["
    "]"
    "("
    ")"
  ] @punctuation.delimiter)

; Shortcut links
(shortcut_link
  [
    "["
    "]"
  ] @punctuation.delimiter)

; ============================================
; TYPEDOWN EXTENSIONS
; ============================================

; Wiki links: [[Page Title]] or [[Page Title|Display Text]]
; Note: In the grammar, [[ and ]] are separate tokens, not double brackets
(wiki_link
  [
    "["
    "]"
  ] @punctuation.bracket)

; Capture the link destination inside wiki_link
(wiki_link
  (link_destination) @text.uri)

; Capture the link text inside wiki_link (for [[dest|text]] format)
(wiki_link
  (link_text) @text.reference)

; Pipe separator in wiki links
(wiki_link
  "|" @punctuation.delimiter)

; Strikethrough (GFM extension)
(strikethrough) @text.strike
