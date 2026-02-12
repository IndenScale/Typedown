# Typedown 集成测试

Integration tests for the Typedown Extension and Python Core.

## 测试结构

```
tests/integration/
├── conftest.py              # 共享 fixtures 和工具
├── test_lsp_server.py       # LSP 服务器协议测试
├── test_compiler_lsp.py     # Compiler + LSP 集成测试
├── test_e2e_scenarios.py    # 端到端场景测试
├── test_vscode_extension.py # VSCode Extension 集成测试
└── README.md                # 本文档
```

## 运行测试

```bash
# 运行所有集成测试
pytest tests/integration/ -v

# 运行特定测试文件
pytest tests/integration/test_lsp_server.py -v
pytest tests/integration/test_compiler_lsp.py -v
pytest tests/integration/test_e2e_scenarios.py -v
pytest tests/integration/test_vscode_extension.py -v

# 运行特定测试类
pytest tests/integration/test_lsp_server.py::TestLSPInitialization -v

# 运行特定测试方法
pytest tests/integration/test_lsp_server.py::TestLSPInitialization::test_server_initializes_with_disk_mode -v

# 使用标记运行
pytest tests/integration/ -v -m "slow"

# 并行运行 (需要 pytest-xdist)
pytest tests/integration/ -v -n auto
```

## 测试类别

### LSP Server 测试 (`test_lsp_server.py`)

测试 LSP 服务器的协议实现：
- 初始化握手
- 文档生命周期事件
- 错误处理
- 服务器状态管理

### Compiler + LSP 集成测试 (`test_compiler_lsp.py`)

测试 Compiler 与 LSP 的集成：
- 状态同步
- 诊断信息流
- 增量编译
- 错误恢复

### 端到端场景测试 (`test_e2e_scenarios.py`)

模拟真实用户工作流：
- 新用户入门
- 团队协作
- 重构工作流
- 复杂项目结构

### VSCode Extension 测试 (`test_vscode_extension.py`)

测试 VSCode Extension 行为：
- 服务器生命周期
- 配置处理
- 文档同步
- 性能特性

## Fixtures

### `lsp_server_instance`

创建一个未初始化的 LSP 服务器实例。

```python
async def test_something(lsp_server_instance):
    server = lsp_server_instance
    # 测试未初始化的服务器
```

### `lsp_pair`

创建已连接的 LSP 客户端-服务器对。

```python
async def test_with_server(lsp_pair, simple_project):
    await lsp_pair.initialize(client_capabilities)
    await lsp_pair.open_document("test.md", "# Content")
    completions = await lsp_pair.request_completion("test.md", 0, 2)
```

### `integration_project`

创建临时测试项目。

```python
def test_project(integration_project):
    (integration_project
        .add_config()
        .add_model("User", "name: str")
        .add_entity("User", "alice", {"name": "Alice"}))
```

### `simple_project`

预配置的简单项目（包含 User 和 Post 模型）。

```python
async def test_with_simple_project(lsp_pair, simple_project):
    await lsp_pair.initialize(client_capabilities)
    # simple_project 已包含基本模型和实体
```

## 编写新测试

```python
import pytest
import asyncio

class TestMyFeature:
    """描述这个测试类的作用."""
    
    @pytest.mark.asyncio
    async def test_specific_behavior(self, lsp_pair, integration_project):
        """测试描述."""
        # 准备项目
        (integration_project
            .add_config()
            .add_model("Test", "field: str"))
        
        # 初始化 LSP
        await lsp_pair.initialize(client_capabilities=None)
        
        # 执行操作
        await lsp_pair.open_document("test.md", "# Test")
        
        # 等待异步处理
        await asyncio.sleep(0.6)
        
        # 验证结果
        assert lsp_pair.server.compiler is not None
```

## 注意事项

1. **异步测试**: 所有 LSP 测试都是异步的，使用 `@pytest.mark.asyncio`
2. **等待时间**: 诊断有 500ms 的防抖，测试中使用 `await asyncio.sleep(0.6)`
3. **临时文件**: 测试自动清理临时目录
4. **并发安全**: LSP 服务器使用锁保护 compiler 状态

## 调试技巧

```python
# 打印编译器状态
print(lsp_pair.server.compiler.source_provider)

# 检查符号表
print(lsp_pair.server.compiler.symbol_table)

# 查看诊断信息
print(lsp_pair.server.compiler.diagnostics)
```

## CI 集成

GitHub Actions 示例:

```yaml
- name: Run Integration Tests
  run: |
    uv sync --extra server
    pytest tests/integration/ -v --tb=short
```
