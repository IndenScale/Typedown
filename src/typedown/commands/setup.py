"""
Setup commands for IDE integrations.
Currently supports: Zed
"""

import json
import os
from pathlib import Path
from typing import Optional

import typer

app = typer.Typer(help="Setup IDE integrations for Typedown")


def get_zed_settings_path() -> Optional[Path]:
    """Get the Zed settings.json path based on OS."""
    home = Path.home()

    if os.name == "nt":  # Windows
        config_dir = home / "AppData" / "Roaming" / "Zed"
    elif os.uname().sysname == "Darwin":  # macOS
        config_dir = home / "Library" / "Application Support" / "Zed"
    else:  # Linux
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            config_dir = Path(xdg_config) / "zed"
        else:
            config_dir = home / ".config" / "zed"

    return config_dir / "settings.json"


def get_typedown_binary_config() -> dict:
    """Get the appropriate binary configuration for Typedown LSP."""
    # Priority: uv tool run > uv run > typedown direct
    import shutil

    if shutil.which("uv"):
        return {"path": "uv", "arguments": ["tool", "run", "typedown", "lsp"]}
    elif shutil.which("typedown"):
        return {"path": "typedown", "arguments": ["lsp"]}
    else:
        return {"path": "python", "arguments": ["-m", "typedown", "lsp"]}


def setup_zed():
    """Setup Zed editor integration."""
    settings_path = get_zed_settings_path()

    if not settings_path:
        typer.echo("Error: Could not determine Zed settings path.", err=True)
        raise typer.Exit(code=1)

    # Ensure directory exists
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    # Read existing settings or create new
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Remove comments (Zed allows comments in JSON)
                lines = [
                    line
                    for line in content.split("\n")
                    if not line.strip().startswith("//")
                ]
                settings = json.loads("\n".join(lines))
        except json.JSONDecodeError:
            typer.echo(f"Error: {settings_path} contains invalid JSON.", err=True)
            raise typer.Exit(code=1)
    else:
        settings = {}

    # Typedown configuration
    binary_config = get_typedown_binary_config()

    typedown_lsp_config = {"binary": binary_config}

    # Update settings
    if "lsp" not in settings:
        settings["lsp"] = {}

    settings["lsp"]["typedown"] = typedown_lsp_config

    # Configure file types if not already set
    if "file_types" not in settings:
        settings["file_types"] = {}

    # Add .td extension to Markdown
    if "Markdown" not in settings["file_types"]:
        settings["file_types"]["Markdown"] = ["td", "typedown"]
    elif "td" not in settings["file_types"]["Markdown"]:
        if isinstance(settings["file_types"]["Markdown"], list):
            settings["file_types"]["Markdown"].extend(["td", "typedown"])
        else:
            settings["file_types"]["Markdown"] = ["td", "typedown"]

    # Configure language servers for Markdown
    if "languages" not in settings:
        settings["languages"] = {}

    if "Markdown" not in settings["languages"]:
        settings["languages"]["Markdown"] = {}

    # Add typedown to language servers
    existing_servers = settings["languages"]["Markdown"].get("language_servers", [])
    if isinstance(existing_servers, list) and "typedown" not in existing_servers:
        # Insert typedown before "..." if it exists
        if "..." in existing_servers:
            idx = existing_servers.index("...")
            existing_servers.insert(idx, "typedown")
        else:
            existing_servers.insert(0, "typedown")
        settings["languages"]["Markdown"]["language_servers"] = existing_servers

    # Write settings back
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

    typer.echo("✅ Zed integration configured successfully!")
    typer.echo("")
    typer.echo(f"Settings written to: {settings_path}")
    typer.echo("")
    typer.echo("Configuration:")
    typer.echo("  - LSP Server: typedown")
    typer.echo(
        f"  - Binary: {binary_config['path']} {' '.join(binary_config['arguments'])}"
    )
    typer.echo("  - File types: .td, .typedown → Markdown")
    typer.echo("")
    typer.echo("Next steps:")
    typer.echo("  1. Restart Zed or run 'zed: reload settings'")
    typer.echo("  2. Open a .td file to start using Typedown")


@app.command()
def zed(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be done without making changes"
    ),
):
    """
    Setup Zed editor integration for Typedown.

    This command configures Zed to:
    - Recognize .td files as Markdown
    - Start Typedown LSP server for .td files
    - Enable wiki link navigation, diagnostics, and completions
    """
    if dry_run:
        settings_path = get_zed_settings_path()
        binary_config = get_typedown_binary_config()

        typer.echo("🔍 Dry run mode - no changes will be made")
        typer.echo("")
        typer.echo(f"Target settings file: {settings_path}")
        typer.echo("")
        typer.echo("Would add:")
        typer.echo(f"  LSP config: typedown -> {binary_config}")
        typer.echo("  File types: .td, .typedown -> Markdown")
        typer.echo("  Language servers: typedown added to Markdown")
        return

    setup_zed()


@app.command()
def status():
    """Show the setup status for all supported editors."""
    typer.echo("Typedown IDE Integration Status")
    typer.echo("=" * 40)
    typer.echo("")

    # Check Zed
    zed_path = get_zed_settings_path()
    if zed_path and zed_path.exists():
        try:
            with open(zed_path, "r") as f:
                content = f.read()
                lines = [
                    line
                    for line in content.split("\n")
                    if not line.strip().startswith("//")
                ]
                settings = json.loads("\n".join(lines))

            has_typedown = "typedown" in settings.get("lsp", {})

            if has_typedown:
                typer.echo("🟢 Zed: Configured")
                binary = settings["lsp"]["typedown"].get("binary", {})
                typer.echo(
                    f"   Binary: {binary.get('path', 'unknown')} {' '.join(binary.get('arguments', []))}"
                )
            else:
                typer.echo("🟡 Zed: Settings exist but Typedown not configured")
                typer.echo("   Run: typedown setup zed")
        except Exception:
            typer.echo("🔴 Zed: Settings file exists but cannot be parsed")
    else:
        typer.echo("⚪ Zed: Not configured")
        typer.echo("   Run: typedown setup zed")

    typer.echo("")

    # Check VS Code (optional, for reference)
    if os.name == "nt":
        _ = Path.home() / "AppData" / "Roaming" / "Code" / "User"
    elif os.uname().sysname == "Darwin":
        _ = (
            Path.home() / "Library" / "Application Support" / "Code" / "User"
        )

    vscode_ext_dir = Path.home() / ".vscode" / "extensions"
    typedown_ext = list(vscode_ext_dir.glob("typedown*"))

    if typedown_ext:
        typer.echo("🟢 VS Code: Extension installed")
    else:
        typer.echo("⚪ VS Code: Extension not installed (optional)")


# Main entry point for `typedown setup`
setup_cmd = app
