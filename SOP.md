# Deployment SOP (Standard Operating Procedure)

此文档记录了在推送代码（Git Push）之前必须执行的检查步骤，以确保 CI/CD 流程顺利运行。

## 1. 依赖管理检查 (Dependency Management)

最常见的 CI 错误是 `npm ci` 失败，原因是 `package.json` 和 `package-lock.json` 不一致。

*   **操作步骤**:
    1.  进入 `website` 目录：`cd website`
    2.  如果修改了 `package.json`，**必须**运行 `npm install` 更新锁文件。
    3.  **强制同步**: 如果遇到 `npm ci` 报错 "Missing ... from lock file" 或 "EUSAGE"，请执行以下彻底清理命令：
        ```bash
        rm -rf node_modules package-lock.json
        npm install
        ```
    4.  **检查点**: 确保 `package-lock.json` 已包含在 Git 暂存区中 (`git add website/package-lock.json`)。

## 2. 代码质量检查 (Linting)

在本地发现并修复代码错误，避免 CI 失败。

*   **操作步骤**:
    ```bash
    npm run lint
    ```
*   **要求**: 必须修复所有 Error 级别的报错。Warning 级别建议修复。

## 3. 构建验证 (Build Verification)

Next.js 的静态导出 (Static Export) 对动态路由有严格要求，容易遗漏 `generateStaticParams`。

*   **操作步骤**:
    ```bash
    npm run build
    ```
*   **常见错误**:
    *   `Error: Page "..." is missing "generateStaticParams()"`: 动态路由页面必须实现此函数。
    *   `Error: API routes are not supported`: 静态导出模式下 API 路由需要配置 `export const dynamic = 'force-static'`。

## 4. 提交前最终检查 (Pre-commit Checklist)

*   [ ] `website/package-lock.json` 是否已更新并添加到暂存区？
*   [ ] 本地 `npm run lint` 是否通过？
*   [ ] 本地 `npm run build` 是否成功？
*   [ ] 是否有未跟踪的新文件（如新组件）？使用 `git status` 确认。

## 常见问题处理

*   **@swc/helpers 缺失**: 如果 CI 报错 `Missing: @swc/helpers`，尝试显式安装该依赖：`npm install @swc/helpers@latest` 并提交。
*   **GitHub Pages 404**: 部署成功后通常需要 10-30 分钟 DNS 才会生效。检查 `website/public/CNAME` 是否正确。
