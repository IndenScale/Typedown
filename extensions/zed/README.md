# Typedown for Zed

Progressive Formalization for Markdown - Zed Editor Support

## Features

- 🎨 **Syntax Highlighting**: Full support for Typedown syntax (`.td` files)
- 🔗 **Wiki Link Navigation**: Jump to entity definitions with `gd` or `Cmd+Click`
- 📐 **Code Folding**: Fold model, entity, spec, and config blocks
- 📋 **Outline View**: See document structure in Zed's outline panel
- 🔍 **LSP Integration**: Real-time validation, completions, and diagnostics

## Installation

### Quick Setup (Recommended)

Install Typedown CLI and run the setup command:

```bash
# Install Typedown
uv tool install typedown

# One-click Zed setup
typedown setup zed
```

This command will:

- ✅ Configure Typedown LSP server in Zed
- ✅ Associate `.td` files with Markdown
- ✅ Enable wiki link navigation and diagnostics

Then restart Zed and open any `.td` file!

### Method 1: Dev Extension (Better Syntax Highlighting)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/IndenScale/Typedown.git
   cd Typedown/extensions/zed
   ```

2. **Install in Zed:**

   ```bash
   # In the zed extension directory
   zed: install dev extension .
   ```

   Or manually:
   - Open Zed
   - `Cmd+Shift+P` → "zed: install dev extension"
   - Select `extensions/zed` directory

3. **Run setup command:**
   ```bash
   typedown setup zed
   ```

### Method 2: Manual Configuration (No CLI Setup)

If you prefer not to install the extension, you can use pure LSP configuration:

```json
{
  "lsp": {
    "typedown": {
      "binary": {
        "path": "uv",
        "arguments": ["tool", "run", "typedown", "lsp"]
      }
    }
  },
  "file_types": {
    "Markdown": ["td"]
  },
  "languages": {
    "Markdown": {
      "language_servers": ["typedown", "..."]
    }
  }
}
```

## Project-Level Configuration

For project-specific settings, create `.zed/settings.json`:

```json
{
  "lsp": {
    "typedown": {
      "binary": {
        "path": "uv",
        "arguments": ["run", "--extra", "server", "typedown", "lsp"]
      }
    }
  }
}
```

## Usage

### Wiki Link Navigation

```typedown
This task is assigned to [[user-alice-v1]].
                              ^
                              └─ Press 'gd' or Cmd+Click to jump
```

| Key      | Action           |
| -------- | ---------------- |
| `gd`     | Go to definition |
| `gr`     | Find references  |
| `Ctrl+o` | Jump back        |

### Available LSP Features

- ✅ Diagnostics (validation errors)
- ✅ Auto-completion (entity IDs, field names)
- ✅ Hover information
- ✅ Go to definition
- ✅ Find references
- ✅ Document symbols

## Troubleshooting

### LSP Server Not Starting

1. Check Typedown is installed:

   ```bash
   typedown --version
   ```

2. Test LSP manually:

   ```bash
   typedown lsp
   # Should start without errors
   ```

3. Check Zed logs:
   - `Cmd+Shift+P` → "zed: open log"

### Wiki Links Not Working

- Ensure cursor is inside `[[...]]`
- Check the entity ID exists (run `typedown check .`)
- Verify the LSP server is running (check Zed status bar)

## Development

To modify this extension:

1. **Build the Rust extension:**

   ```bash
   cd extensions/zed
   cargo build --release
   ```

2. **Install as dev extension in Zed:**
   - Open Zed
   - `Cmd+Shift+P` → "zed: install dev extension"
   - Select `extensions/zed` directory

3. **Reload and test:**
   - `Cmd+Shift+P` → "zed: reload extensions"
   - Test changes

### Project Structure

```
extensions/zed/
├── Cargo.toml              # Rust package configuration
├── src/
│   └── lib.rs              # Extension code (LSP integration)
├── extension.toml          # Extension manifest
└── languages/
    └── typedown/
        ├── config.toml     # Language configuration
        ├── highlights.scm  # Syntax highlighting queries
        ├── brackets.scm    # Bracket matching
        ├── indents.scm     # Indentation rules
        ├── injections.scm  # Language injections
        └── outline.scm     # Outline/structure view
```

## License

MIT © [IndenScale](https://github.com/IndenScale)
