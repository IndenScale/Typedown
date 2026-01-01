"""
td run 命令：执行脚本系统
"""

import typer
from pathlib import Path
from rich.console import Console
from typedown.core.compiler import Compiler


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
    console = Console()
    
    try:
        # 如果目标是目录，需要先编译以加载文档
        compiler = Compiler(target, console)
        
        # 如果目标是文件，先解析该文件
        if target.is_file():
            # 使用 lint 来加载文档（最轻量级的编译）
            compiler.lint(target)
        
        # 执行脚本
        exit_code = compiler.run_script(script_name, target, dry_run)
        
        if exit_code == 0:
            console.print(f"[bold green]✓[/bold green] Script '{script_name}' completed successfully")
        else:
            console.print(f"[bold red]✗[/bold red] Script '{script_name}' failed with exit code {exit_code}")
        
        raise typer.Exit(code=exit_code)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
