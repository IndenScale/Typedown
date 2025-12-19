# 脚手架 (Scaffolding)

此目录包含用于自动化维护 Headerless ERP 的工具链。

## 规划功能

### 1. 结构生成器 (Structure Generators)

- `gen_month.py`: 自动生成新的月份账本目录。
- `gen_dept.py`: 自动初始化新部门的 `governance` 和 `collaboration` 目录。

### 2. Marketplace Client

- 能够拉取行业通用的标准模型 (如 ISO 20022 金融报文标准)。

### 3. 可视化配置 (Visualization)

- `spa_config.json`: 定义前端 Dashboard 如何读取 `ledgers` 目录中的数据并进行渲染。
