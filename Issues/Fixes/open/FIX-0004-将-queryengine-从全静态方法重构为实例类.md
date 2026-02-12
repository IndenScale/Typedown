---
id: FIX-0004
uid: eee5c3
type: fix
status: open
stage: doing
title: 将 QueryEngine 从全静态方法重构为实例类
created_at: '2026-02-12T09:41:26'
updated_at: '2026-02-12T10:06:46'
parent: EPIC-0000
dependencies: []
related:
- FIX-0003
domains:
- architecture
tags:
- '#EPIC-0000'
- '#FIX-0004'
files:
- src/typedown/core/analysis/query.py
- src/typedown/core/analysis/validator.py
- src/typedown/core/analysis/spec_executor.py
- src/typedown/core/services/query_service.py
- tests/core/analysis/test_query.py
- tests/core/analysis/test_query_identifier_integration.py
- tests/core/analysis/test_hash_addressing.py
- tests/integration/test_query_engine.py
- tests/integration/test_sql_query.py
criticality: high
solution: implemented # implemented, cancelled, wontfix, duplicate
opened_at: '2026-02-12T09:41:26'
---

## FIX-0004: 将 QueryEngine 从全静态方法重构为实例类

## Objective
`QueryEngine` 当前是一个完全由静态方法组成的类，实际上只是一个函数命名空间。这种设计存在以下问题：
1. 无法存储状态（如缓存、配置）
2. 难以进行单元测试（无法 mock）
3. 违反面向对象设计原则
4. 每次调用需要传递 symbol_table 等参数

本 Issue 将其重构为实例类，提升可测试性和可扩展性。

## Problem Description

### 当前设计问题
```python
# src/typedown/core/analysis/query.py

class QueryError(Exception):  # 重复定义！
    pass

class QueryEngine:
    @staticmethod
    def execute_sql(query: str, symbol_table: Any, ...) -> List[Any]:
        ...
    
    @staticmethod
    def evaluate_data(data: Any, symbol_table: Any, ...) -> Any:
        ...
    
    @staticmethod
    def resolve_string(text: str, symbol_table: Any, ...) -> Any:
        ...
    
    @staticmethod
    def resolve_query(query: str, symbol_table: Any, ...) -> List[Any]:
        ...
    
    # ... 更多静态方法
```

### 具体坏味道
1. **重复的错误类定义** (Line 20)
   - `query.py` 内部定义了 `QueryError`
   - 同时从 `errors.py` 导入 `QueryError`
   - 造成命名冲突和混淆

2. **每次调用传递相同参数**
   ```python
   QueryEngine.evaluate_data(data, symbol_table, context_path)
   QueryEngine.resolve_string(text, symbol_table, context_path)
   # 参数重复传递，效率低且易错
   ```

3. **无法注入依赖**
   - 无法为 QueryEngine 注入 mock symbol_table 进行测试
   - 无法添加查询缓存等优化

## Proposed Design

### 新设计
```python
from typing import Optional
from pathlib import Path

class QueryEngine:
    """
    QueryEngine with instance-based design.
    
    Usage:
        engine = QueryEngine(symbol_table, root_dir)
        result = engine.resolve_query("User.alice")
    """
    
    def __init__(
        self, 
        symbol_table: SymbolTable,
        root_dir: Optional[Path] = None,
        resources: Optional[Dict[str, Any]] = None
    ):
        self.symbol_table = symbol_table
        self.root_dir = root_dir
        self.resources = resources or {}
        self._cache: Dict[str, Any] = {}  # 可添加缓存
    
    def execute_sql(self, query: str, parameters: Dict[str, Any] = {}) -> List[Any]:
        # 使用 self.symbol_table
        ...
    
    def evaluate_data(self, data: Any, context_path: Optional[Path] = None) -> Any:
        # 使用 self.symbol_table
        ...
    
    def resolve_string(self, text: str, context_path: Optional[Path] = None) -> Any:
        ...
    
    def resolve_query(
        self, 
        query: str, 
        scope: Optional[Path] = None,
        context_path: Optional[Path] = None
    ) -> List[Any]:
        ...
    
    def clear_cache(self) -> None:
        """Clear internal cache."""
        self._cache.clear()
```

### 错误类统一
```python
# 删除 query.py 内部的 QueryError 定义
# 统一从 typedown.core.base.errors 导入
from typedown.core.base.errors import QueryError, ReferenceError
```

## Acceptance Criteria
- [ ] `QueryEngine` 改为实例类，支持 `__init__` 初始化
- [ ] 删除 `query.py` 内部重复的 `QueryError` 定义
- [ ] 所有静态方法改为实例方法
- [ ] 实例化时注入 `symbol_table`、`root_dir`、`resources`
- [ ] 所有调用处更新为新 API
- [ ] 所有测试通过
- [ ] 新增 QueryEngine 的单元测试（mock symbol_table）

## Technical Tasks

### Phase 1: 重构 QueryEngine 类
- [ ] 修改 `src/typedown/core/analysis/query.py`
  - [ ] 删除内部的 `QueryError` 定义
  - [ ] 添加 `__init__` 方法
  - [ ] 将所有 `@staticmethod` 改为实例方法
  - [ ] 更新方法签名，移除 `symbol_table` 参数
  - [ ] 方法内部使用 `self.symbol_table`

### Phase 2: 更新调用方
- [ ] 更新 `src/typedown/core/analysis/validator.py`
  ```python
  # 修改前
  resolved = QueryEngine.evaluate_data(current_data, symbol_table, context_path)
  
  # 修改后
  engine = QueryEngine(symbol_table)
  resolved = engine.evaluate_data(current_data, context_path)
  ```

- [ ] 更新 `src/typedown/core/compiler.py`
  ```python
  # 在 query() 方法中
  engine = QueryEngine(self.symbol_table, self.project_root)
  return engine.resolve_query(query_string, context_path=ctx)
  ```

- [ ] 搜索并更新其他可能的调用

### Phase 3: 测试
- [ ] 更新现有测试
- [ ] 新增 QueryEngine 单元测试
  - [ ] 测试初始化
  - [ ] 测试查询功能
  - [ ] 测试 mock symbol_table

## Migration Guide

### 旧 API
```python
from typedown.core.analysis.query import QueryEngine

results = QueryEngine.resolve_query("User.alice", symbol_table, root_dir=project_root)
data = QueryEngine.evaluate_data(raw_data, symbol_table)
```

### 新 API
```python
from typedown.core.analysis.query import QueryEngine

engine = QueryEngine(symbol_table, root_dir=project_root)
results = engine.resolve_query("User.alice")
data = engine.evaluate_data(raw_data)
```

## Affected Files
```
src/typedown/core/analysis/query.py         # 重构
src/typedown/core/analysis/validator.py     # 更新调用
src/typedown/core/compiler.py               # 更新调用
tests/core/analysis/test_query.py           # 更新/新增测试
```

## Review Comments
