# Language Server Protocol (LSP)

To support multiple editors (VS Code, Neovim, IntelliJ), Typedown implements a standard LSP service.

## Feature Implementation

*   `textDocument/completion`: Provide Schema-based field completion.
*   `textDocument/definition`: Handle jump to definition.
*   `textDocument/hover`: Show preview of Entity's resolved complete data.
*   `textDocument/publishDiagnostics`: Push compilation errors.

The LSP service reuses the core logic of the `tdc` compiler.
