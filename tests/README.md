# Typedown Test Suite

Typedown 测试套件，包含单元测试和集成测试。

## 目录结构

```
tests/
├── fixtures/               # 测试夹具
│   ├── lint_test.td        # Lint 测试用例
│   ├── spec_test.td        # Spec 测试用例
│   └── script_test.td      # 脚本测试用例
├── unit/                   # 单元测试
│   ├── 01_model_and_entity/# 模型与实体测试
│   ├── 02_validation/      # 验证规则测试
│   ├── 03_evolution/       # 演进语义测试
│   ├── 04_config/          # 配置系统测试
│   ├── 05_references/      # 引用系统测试
│   ├── 06_scripts/         # 脚本系统测试
│   └── 07_error_codes/     # 错误码覆盖测试
├── integration/            # 集成测试
├── conftest.py             # pytest 配置
└── README.md               # 本文档
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单元测试
pytest tests/unit/ -v

# 运行特定模块
pytest tests/unit/01_model_and_entity/ -v

# 运行集成测试
pytest tests/integration/ -v
```

## 从旧路径迁移

原 `test/` → `tests/`  
原 `test_project/` → `tests/fixtures/`
