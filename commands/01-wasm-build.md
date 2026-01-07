# SOP: 构建 WASM 核心

## 目标

将最新的 Python 源代码 (`src/typedown`) 打包为 WebAssembly 兼容的 Wheel 文件，以供浏览器端的 Playground 使用。

## 背景

网站的 Playground 通过 Pyodide 运行完整的 Python 环境。为了避免浏览器缓存和版本混乱问题，它需要一个固定命名为 `typedown-0.0.0-py3-none-any.whl` 的特殊 Wheel 文件。

## 执行动作

运行以下脚本：

```bash
./scripts/sop_build_wasm.sh
```

## 验证标准

- 检查 `website/public/typedown-0.0.0-py3-none-any.whl` 文件是否已更新（查看文件修改时间）。
- (可选) 在本地启动网站，验证 Playground 能否正常加载并运行 Python 代码。
