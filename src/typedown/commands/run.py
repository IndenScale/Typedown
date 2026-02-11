"""
td run 命令：执行脚本系统
"""

import typer
from pathlib import Path

from typedown.commands.context import cli_session
from typedown.commands.output import cli_result, cli_error, cli_success


def run(
    script_name: str = typer.Argument(..., help="脚本名称（如 'validate', 'verify-business'）"),
    target: Path = typer.Argument(
        Path.cwd(),
        help="目标文件或目录（默认为当前目录）",
        exists=True
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="仅打印命令而不执行"
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON"
    )
):
    """
    Execute defined scripts (Script System).
    
    查找顺序（就近原则）：
    1. File Scope: 目标文件的 Front Matter
    2. Directory Scope: 目录的 config.td
    3. Project Scope: typedown.yaml
    
    示例：
    
        # 执行当前文件的 validate 脚本
        $ td run validate user_profile.td
        
        # 批量执行 specs/ 目录下所有文件的 test 脚本
        $ td run test specs/
        
        # 仅打印命令而不执行
        $ td run validate user_profile.td --dry-run
    """
    with cli_session(target, as_json=as_json, require_project=True) as ctx:
        # 如果目标是文件，先解析该文件
        if target.is_file():
            # 使用 lint 来加载文档（最轻量级的编译）
            ctx.compiler.lint(target)
        
        # 执行脚本
        exit_code = ctx.compiler.run_script(script_name, target, dry_run)
        
        if as_json:
            cli_result(ctx, {
                "script": script_name,
                "target": str(target),
                "exit_code": exit_code,
                "dry_run": dry_run
            }, exit_on_error=False)
        else:
            if exit_code == 0:
                cli_success(ctx, f"Script '{script_name}' completed successfully")
            else:
                ctx.display_console.print(f"[bold red]✗[/bold red] Script '{script_name}' failed with exit code {exit_code}")
        
        if exit_code != 0:
            raise typer.Exit(code=exit_code)
