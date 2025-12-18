# CLI Reference

The `td` command-line tool is the primary interface for Typedown.

## `td test`

Runs the validation and testing pipeline.

**Usage:**
```bash
td test [PATH] [OPTIONS]
```

**Arguments:**
*   `PATH`: The file or directory to test. Defaults to current directory `.`

**Options:**
*   `--tag`, `-t`: Filter specs by tag (if supported).

## `td lsp`

Starts the Language Server Protocol (LSP) server. This is typically used by IDE extensions (like VS Code) and not run manually.

## `td build`

(Experimental) Compiles the documentation into other formats.

## `td debug`

(Internal) Tools for debugging the AST and parser.
