# SOP: 发布流程

## 目标
升级项目版本号，更新所有相关配置文件，并创建 Git 标签。

## 背景
*   **涉及文件**: `pyproject.toml` (核心) 和 `extensions/vscode/package.json` (插件)。
*   **版本策略**: 遵循语义化版本 (SemVer)。
    *   `patch` (补丁):用于 Bug 修复或微小调整。
    *   `minor` (次版本): 用于新功能发布。

## 执行动作
根据更新类型（`patch` 或 `minor`），运行以下命令之一：

\`\`\`bash
# 补丁更新 (例如 0.2.14 -> 0.2.15)
./scripts/sop_release.sh patch

# 次版本更新 (例如 0.2.14 -> 0.3.0)
./scripts/sop_release.sh minor
\`\`\`

## 后续操作
1.  **验证**: 运行 `git status` 确认脚本已自动创建了 Commit 和 Tag。
2.  **推送**: 手动执行（或询问用户）：`git push && git push --tags`。
