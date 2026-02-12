; Typedown block syntax highlighting - Extended from Markdown

; Headings
(atx_heading
  (inline) @text.title)

(setext_heading
  (paragraph) @text.title)

; Heading markers
[
  (atx_h1_marker)
  (atx_h2_marker)
  (atx_h3_marker)
  (atx_h4_marker)
  (atx_h5_marker)
  (atx_h6_marker)
  (setext_h1_underline)
  (setext_h2_underline)
] @punctuation.special

; Code blocks
[
  (link_title)
  (indented_code_block)
  (fenced_code_block)
] @text.literal

(fenced_code_block_delimiter) @punctuation.delimiter

(code_fence_content) @none

(link_destination) @text.uri

(link_label) @text.reference

; List markers
[
  (list_marker_plus)
  (list_marker_minus)
  (list_marker_star)
  (list_marker_dot)
  (list_marker_parenthesis)
  (thematic_break)
] @punctuation.special

; Block quotes and continuation
[
  (block_continuation)
  (block_quote_marker)
] @punctuation.special

; Escape sequences
(backslash_escape) @string.escape

; ============================================
; TYPEDOWN EXTENSIONS
; ============================================

; Typedown code blocks with special language markers
; ```model:EntityName
; ```entity:EntityName
; ```spec:SpecName
; ```config:ConfigName
(fenced_code_block
  (info_string
    (language) @keyword.special))

; Model blocks - highlighted as code blocks but with special keyword
(fenced_code_block
  (info_string
    (language) @_lang
    (#match? @_lang "^(model|entity|spec|config)"))
  (code_fence_content) @text.literal)

; Metadata blocks (YAML frontmatter)
(minus_metadata) @text.literal
(plus_metadata) @text.literal

; Table support (GFM)
(pipe_table) @text.table
(pipe_table_header) @text.title
(pipe_table_delimiter_row) @punctuation.special
(pipe_table_cell) @text

; HTML blocks
(html_block) @text.html
