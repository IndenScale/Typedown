# EGI PoC - Typedown 工程建模演示

> 本目录演示 Typedown 在企业级工程场景中的应用潜力，通过递进式案例展示从简单物理约束到复杂工程系统的建模能力。

## 项目架构

```
egi/
├── README.td                        # 整体架构说明
├── 01_Introduction/                 # 基础原理演示
│   ├── models/
│   │   ├── primitives.td            # 基本数据类型 (Vector3, Dimension, Material)
│   │   ├── physics.td               # 物理约束建模 (BoundingBox, Load, Support)
│   │   └── validation.td            # 三层验证体系说明
│   └── entities/
│       ├── simple_beam.td           # 简支梁承重计算
│       └── block_stacking.td        # 方块堆叠碰撞检测
│
└── 02_IT-Deploy&Integration/        # IT 设备上架建模
    ├── models/
    │   ├── equipment.td             # 设备 (Server, Switch, PDU)
    │   ├── cabinet.td               # 机柜 (槽位、承重、功耗)
    │   └── cable.td                 # 线缆 (类型、长度、端口)
    ├── specs/
    │   └── constraints.td           # 全局约束验证 (Spec)
    └── entities/
        ├── standard_cabinet.td      # 42U 标准机柜
        ├── deployment_plan.td       # 完整上架方案
        └── validation_report.td     # 约束验证报告
```

## 递进关系

### 01 → 02 的能力跃迁

| 维度 | 01 Introduction | 02 IT-Deploy |
|------|-----------------|--------------|
| **Model 复杂度** | 简单几何体 + 基础物理 | 多品类设备 + 多维度约束 |
| **Reference 类型** | 一对一空间引用 | 多对多拓扑关系（设备-机柜-线缆） |
| **Spec 层级** | 字段级、模型级 | 全局级跨模型验证 |
| **约束类型** | 静态约束（碰撞、承重） | 动态约束（功耗预算、线缆长度、冗余） |
| **验证场景** | 单实体自洽 | 多实体关联一致性 |

## Typedown 核心概念映射

### Model → 工程模板

```model:Example
class Example(BaseModel):
    # 使用 Pydantic 定义数据结构
    field: str = Field(..., pattern=r'^[A-Z]+$')
```

### Entity → 具体实例

```entity Example:my-example
field: "VALUE"
```

### Reference → 关系连接

使用 `[[entity-id]]` 语法建立实体间关系：

```yaml
material: [[steel-q235]]
equipments:
  - [[server-01]]
  - [[server-02]]
```

### Spec → 约束验证

```spec:example_check
@target(type="PhysicalObject", scope="local")
def example_check(subject: PhysicalObject):
    """示例验证"""
    assert subject.name, "名称不能为空"
```

## 快速开始

```bash
# 验证 01 Introduction
cd 01_Introduction && typedown check .

# 验证 02 IT-Deploy
cd "02_IT-Deploy&Integration" && typedown check .

# 生成验证报告
typedown validate --format markdown
```

## 设计哲学

这两个 PoC 共同展示 Typedown 的**渐进式形式化**理念：

1. **从简单开始**: 用几何方块理解基本建模概念
2. **逐步复杂**: 引入真实工程中的多维度约束
3. **保持可读**: 即使是复杂场景，.td 文件仍对人类友好
4. **验证先行**: 在问题发生前通过 Spec 捕获设计错误

---

> 💡 **提示**: 建议按 01 → 02 的顺序阅读，理解 Typedown 如何从简单的物理建模延伸到复杂的工程系统。
