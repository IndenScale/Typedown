# SOP: 预发布验证

## 目标
在正式发布前，验证 Python 核心库与 VS Code 插件的功能完整性。

## 背景
我们必须确保核心库的修改不会破坏插件功能，并且核心库本身必须通过所有单元测试。

## 执行动作
运行以下脚本：

\`\`\`bash
./scripts/sop_pre_release.sh
\`\`\`

## 验证标准
*   **Python 测试**: 所有的 `pytest` 测试用例必须全部通过 (PASS)。
*   **插件编译**: `extensions/vscode` 目录下的 `npm run compile` 必须成功执行，无报错。
