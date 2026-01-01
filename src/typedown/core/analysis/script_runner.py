"""
Script Runner: 脚本系统的核心执行引擎

负责：
1. 脚本查找（File → Directory → Project）
2. 环境变量注入（${FILE}, ${DIR}, ${ROOT} 等）
3. 脚本执行与结果报告
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Optional
from rich.console import Console

from typedown.core.base.errors import TypedownError


class ScriptRunner:
    """
    脚本执行器
    
    遵循"就近原则 (Nearest Winner)"：
    1. File Scope: 当前文件的 Front Matter
    2. Directory Scope: 当前目录（及父目录）的 config.td
    3. Project Scope: 根目录的 typedown.yaml
    """
    
    def __init__(
        self,
        project_root: Path,
        console: Optional[Console] = None
    ):
        self.project_root = project_root.resolve()
        self.console = console or Console()
    
    def find_script(
        self,
        script_name: str,
        target_file: Optional[Path] = None,
        file_scripts: Optional[Dict[str, str]] = None,
        dir_scripts: Optional[Dict[str, str]] = None,
        project_scripts: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        查找脚本定义，遵循作用域优先级
        
        Args:
            script_name: 脚本名称（如 "validate", "verify-business"）
            target_file: 目标文件路径（用于 File Scope）
            file_scripts: 文件级别脚本（从 Front Matter 提取）
            dir_scripts: 目录级别脚本（从 config.td 提取）
            project_scripts: 项目级别脚本（从 typedown.yaml 提取）
        
        Returns:
            脚本命令字符串，如果未找到则返回 None
        """
        # L1: File Scope
        if file_scripts and script_name in file_scripts:
            return file_scripts[script_name]
        
        # L2: Directory Scope
        if dir_scripts and script_name in dir_scripts:
            return dir_scripts[script_name]
        
        # L3: Project Scope
        if project_scripts and script_name in project_scripts:
            return project_scripts[script_name]
        
        return None
    
    def inject_env_vars(
        self,
        command: str,
        target_file: Optional[Path] = None
    ) -> str:
        """
        注入环境变量到脚本命令中
        
        支持的变量：
        - ${FILE}: 当前文件的绝对路径
        - ${DIR}: 当前文件所在目录的绝对路径
        - ${ROOT}: 项目根目录
        - ${FILE_NAME}: 不带后缀的文件名
        - ${TD_ENV}: 当前运行环境 (local, ci, prod)
        
        Args:
            command: 原始命令字符串
            target_file: 目标文件路径
        
        Returns:
            注入环境变量后的命令字符串
        """
        env_vars = {
            "ROOT": str(self.project_root),
            "TD_ENV": os.getenv("TD_ENV", "local")
        }
        
        if target_file:
            target_file = target_file.resolve()
            env_vars["FILE"] = str(target_file)
            env_vars["DIR"] = str(target_file.parent)
            env_vars["FILE_NAME"] = target_file.stem
        
        # 替换 ${VAR} 格式的变量
        def replace_var(match):
            var_name = match.group(1)
            if var_name in env_vars:
                return env_vars[var_name]
            # 如果是未知变量，保留原样
            return match.group(0)
        
        return re.sub(r'\$\{(\w+)\}', replace_var, command)
    
    def run_script(
        self,
        script_name: str,
        target_file: Optional[Path] = None,
        file_scripts: Optional[Dict[str, str]] = None,
        dir_scripts: Optional[Dict[str, str]] = None,
        project_scripts: Optional[Dict[str, str]] = None,
        dry_run: bool = False
    ) -> int:
        """
        执行脚本
        
        Args:
            script_name: 脚本名称
            target_file: 目标文件路径
            file_scripts: 文件级别脚本
            dir_scripts: 目录级别脚本
            project_scripts: 项目级别脚本
            dry_run: 是否仅打印命令而不执行
        
        Returns:
            退出码（0 表示成功）
        
        Raises:
            TypedownError: 如果脚本未找到
        """
        # 查找脚本
        command = self.find_script(
            script_name,
            target_file,
            file_scripts,
            dir_scripts,
            project_scripts
        )
        
        if command is None:
            raise TypedownError(
                f"Script '{script_name}' not found in any scope. "
                f"Available scopes: File → Directory → Project"
            )
        
        # 注入环境变量
        command = self.inject_env_vars(command, target_file)
        
        # 打印命令
        self.console.print(f"[bold cyan]Running:[/bold cyan] {command}")
        
        if dry_run:
            self.console.print("[yellow]Dry run mode: Command not executed[/yellow]")
            return 0
        
        # 执行命令
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_root,
                capture_output=False,  # 直接输出到终端
                text=True
            )
            return result.returncode
        except Exception as e:
            self.console.print(f"[bold red]Error executing script:[/bold red] {e}")
            return 1
