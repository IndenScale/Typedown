# SOP: 网站健康检查

## 目标
确保 Next.js 网站代码整洁、依赖完整且可成功构建（静态导出）。

## 背景
Next.js 的静态导出（Static Export）模式非常严格。此外，常见的 CI 失败原因包括：
1. **依赖不一致**：本地添加了新包但未同步更新 `package-lock.json`。
2. **缺失依赖**：代码中引入了包但未执行 `npm install`。
3. **构建约束**：动态路由缺失 `generateStaticParams`。

## 执行动作
运行以下脚本：

\`\`\`bash
./scripts/sop_check_website.sh
\`\`\`

## 内部逻辑说明（供 Agent 审计）
脚本执行以下三个阶段：
1. **依赖审计 (`npm ls`)**：检查 `package.json` 与本地 `node_modules` 是否完全匹配。如果失败，说明依赖树处于损坏或未同步状态。
2. **代码规范 (`npm run lint`)**：静态代码分析。
3. **构建验证 (`npm run build`)**：模拟线上部署的静态导出过程。

## 故障排查
*   **依赖审计失败**: 
    *   **原因**: 通常是由于手动修改了 `package.json` 但未运行 install。
    *   **修复**: 在 `website` 目录下运行 `npm install`。如果问题持续，请尝试 `rm -rf node_modules && npm install`。
*   **Lint 错误**: 请根据报错信息在源代码中修复。
*   **Build 错误**: 
    *   `Page ... missing generateStaticParams`: 必须为动态路由页面实现该函数。
    *   `API routes not supported`: 检查是否有 API 路由未配置为静态导出。
