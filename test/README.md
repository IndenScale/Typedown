# Typedown Aligned Test Suite

测试套件与文档规范对齐，确保实现与文档设计同步。

## 目录结构

```
tests_aligned/
├── 01_model_and_entity/      # 模型与实体测试 (docs/zh/02_concepts/01_model-and-entity.md)
│   ├── test_model_signature.py      # Model 签名严格性
│   ├── test_entity_signature.py     # Entity 签名和 ID 规则
│   ├── test_reference_types.py      # Ref[T] 类型系统
│   └── test_scope_rules.py          # 词法作用域规则
├── 02_validation/            # 验证规则测试 (docs/zh/02_concepts/02_validation.md)
│   ├── test_field_validator.py      # 字段级验证
│   ├── test_model_validator.py      # 模型级验证
│   ├── test_spec_validation.py      # Spec 全局验证
│   └── test_query_and_sql.py        # query() 和 sql() 函数
├── 03_evolution/             # 演进语义测试 (docs/zh/02_concepts/03_evolution.md)
│   ├── test_former_syntax.py        # former 语法
│   └── test_fork_and_convergence.py # 分叉检测和收敛
├── 04_config/                # 配置系统测试 (docs/zh/02_concepts/04_config.md)
│   ├── test_config_block.py         # Config 块
│   ├── test_front_matter.py         # Front Matter
│   └── test_env_variables.py        # 环境变量
├── 05_references/            # 引用系统测试 (docs/zh/03_guides/01_references.md)
│   ├── test_id_reference.py         # ID 引用
│   ├── test_list_reference.py       # 列表引用
│   └── test_type_safety.py          # 类型安全
├── 06_scripts/               # 脚本系统测试 (docs/zh/03_guides/02_scripts.md)
├── 07_error_codes/           # 错误码完整覆盖 (docs/zh/04_reference/01_error-codes.md)
│   └── test_all_error_codes.py      # 所有错误码触发测试
├── integration/              # 端到端集成测试
├── conftest.py               # 共享 fixtures 和工具函数
└── README.md                 # 本文档
```

## 使用方法

```bash
# 运行所有对齐测试
pytest tests_aligned/ -v

# 运行特定模块
pytest tests_aligned/01_model_and_entity/ -v
pytest tests_aligned/02_validation/ -v

# 运行特定测试
pytest tests_aligned/01_model_and_entity/test_model_signature.py::TestModelSignatureStrictness -v

# 仅运行未跳过的测试（排除已知未实现功能）
pytest tests_aligned/ -v --ignore-glob="*skip*"
```

## 测试命名约定

### 成功测试
- `test_valid_{condition}` - 验证有效输入通过
- `test_{feature}_works` - 验证功能正常工作

### 错误测试
- `test_{condition}__should_raise_{error_code}` - 验证特定错误被触发

### 边缘测试
- `test_edge_{condition}` - 验证边缘情况

### 已知限制
- `@pytest.mark.skip(reason="...")` - 标记文档中但尚未实现的功能

## 文档-实现差异追踪

| 差异 | 文档 | 实现 | 测试状态 |
|------|------|------|----------|
| Reference vs Ref 命名 | `Reference[T]` | `Ref["T"]` | 已标记 |
| 多态引用 | `Ref[T1, T2]` | 不支持 | 已跳过 |
| 演进分叉检测 | 要求检测 | 未实现 | 已跳过 |
| 环境变量 | 定义完整 | 待验证 | 已跳过 |
| ID 字符集 | `_`, `-` | 包括 `.` | 已记录 |

## 错误码覆盖状态

| 阶段 | 错误码 | 测试状态 |
|------|--------|----------|
| L1 Scanner | E0101-E0105 | ✅ 已覆盖 |
| L2 Linker | E0221-E0241 | ✅ 已覆盖 |
| L3 Validator | E0341-E0365 | ✅ 已覆盖 |
| L4 Spec | E0421-E0424 | ⚠️ 需 Spec 执行环境 |
| System | E0981-E0983 | ⚠️ 难模拟 |

## 扩展测试

添加新测试时，请遵循以下模式：

```python
"""
Test: {Feature Name}
Related Doc: docs/zh/{path}.md Section "{Section}"
Error Codes: {Error codes if applicable}
"""

import pytest
from tests_aligned.conftest import TestProjectBuilder, assert_error_exists, assert_no_errors

class Test{FeatureName}:
    """Test {feature}."""
    
    def test_valid_{case}(self, project):
        """Test valid {case}."""
        # Arrange
        project.add_config().add_file(...)
        
        # Act
        scan_diag, link_diag, val_diag = project.compile()
        
        # Assert
        assert_no_errors(val_diag)
    
    def test_invalid_{case}__should_raise_{code}(self, project):
        """Test that {case} raises {code}."""
        # Arrange
        project.add_config().add_file(...)
        
        # Act
        scan_diag, link_diag, val_diag = project.compile()
        
        # Assert
        assert_error_exists(val_diag, ErrorCode.{CODE})
```

## 与原文档的关系

每个测试文件头部的 docstring 都包含相关文档的引用，确保：
1. 测试可追溯至文档规范
2. 文档更新时可以找到相关测试
3. 实现与文档不同步时测试会失败
