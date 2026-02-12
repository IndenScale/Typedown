; Outline/Structure view for Typedown
; Shows document structure in Zed's outline panel

; Headings
(atx_heading
  (atx_heading_marker) @_marker
  (heading_content) @name) @item

; Entity blocks appear in outline
(fenced_code_block
  (info_string
    (language) @directive
    (_) @name)
  (#match? @directive "^entity$")) @item

; Model blocks appear in outline
(fenced_code_block
  (info_string
    (language) @directive
    (_) @name)
  (#match? @directive "^model$")) @item

; Spec blocks appear in outline
(fenced_code_block
  (info_string
    (language) @directive
    (_) @name)
  (#match? @directive "^spec$")) @item
