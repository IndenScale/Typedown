---
name: git-reference-manager
description: "安全地引入外部 Git 仓库作为参考资料。负责管理 `_reference` 目录，确保外部代码只读且不污染项目版本控制。"
---

# Git 参考仓库管理 (Git Reference Manager)

本技能指导如何规范地将外部仓库引入到项目中进行阅读和学习。这对于理解第三方库架构或寻找最佳实践至关重要。

## 核心法则

> **隔离原则**：参考代码必须严格隔离在 `_reference/` 目录中，严禁提交到主项目的 Git 历史中。

## 标准工作流

当需要参考外部仓库（例如 `anthropics/skills` 或 `pandas`）时，**必须**严格按顺序执行以下三个步骤：

### 1. 准备隔离区 (Prepare Sandbox)

首先确保用于存放参考资料的专用目录存在。

- **检查**: 项目根目录下是否存在 `_reference` 目录？
- **动作**: 如果不存在，创建它。

  ```bash
  mkdir -p _reference
  ```

### 2. 建立防线 (Secure Boundary)

在拉取任何代码之前，必须确保 Git 会忽略该目录。

- **检查**: `.gitignore` 文件中是否包含 `_reference/`？
- **动作**: 如果没有，追加到文件末尾。

  ```bash
  # 检查
  grep "_reference/" .gitignore
  # 追加 (如果缺失)
  echo -e "\n# External References\n_reference/" >> .gitignore
  ```

### 3. 拉取参考 (Fetch References)

将目标仓库克隆到隔离区内的子目录中。

- **命名**: 使用仓库名作为子目录名。
- **动作**: 使用 `git clone`。

  ```bash
  git clone <REPO_URL> _reference/<REPO_NAME>
  ```

- **注意**: 不需要深度历史，建议使用 `--depth 2` 以节省时间和空间。

  ```bash
  git clone --depth 1 https://github.com/anthropics/skills.git _reference/anthropics_skills
  ```

## 最佳实践

- **只读模式**: 将 `_reference/` 下的所有文件视为**只读**。不要修改它们，除非你是为了测试某些改动（但修改将丢失）。
- **通过 grep 搜索**: 使用 `grep` 或 `ripgrep` 在参考目录中搜索代码模式。
- **随时丢弃**: 既然这些文件被 git 忽略且可以重新克隆，完成任务后可以随时删除它们释放空间。

## 示例

**用户请求**: "我想看看 React 的源码是怎么处理 Hook 的。"

**Agent 执行**:

1. `mkdir -p _reference`
2. `grep "_reference" .gitignore || echo "_reference/" >> .gitignore`
3. `git clone --depth 1 https://github.com/facebook/react.git _reference/react`
4. 开始阅读 `_reference/react/packages/react-reconciler/...`
