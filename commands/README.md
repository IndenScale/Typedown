# Typedown Agent SOP 指令集

本目录包含 Monoco Agent 用于执行日常维护和发布任务的标准作业程序（SOP）。
每个文件代表一个特定的工作流，指导 Agent 如何调用 `scripts/` 目录下的自动化脚本。

## 可用工作流

*   **[01-wasm-build.md](./01-wasm-build.md)**: **构建 WASM 核心**
    *   将 Python 核心代码打包为 WebAssembly 格式，供网站 Playground 使用。
*   **[02-web-check.md](./02-web-check.md)**: **网站健康检查**
    *   验证网站代码的完整性（Lint 检查与静态构建测试）。
*   **[03-pre-release.md](./03-pre-release.md)**: **预发布验证**
    *   在发布前运行全面的核心测试与插件编译检查。
*   **[04-release.md](./04-release.md)**: **发布流程**
    *   自动升级版本号、更新配置文件、创建 Git 标签并准备推送。

## 使用原则

Agent 应首先读取具体的 `.md` 指南文件以理解上下文和目标，然后执行其中指定的 `scripts/` 脚本。
