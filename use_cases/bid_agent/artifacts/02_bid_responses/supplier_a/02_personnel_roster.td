# 供应商 A - 项目人员配置表

```config:python
from use_cases.bid_agent.models.evidence import Person
```

## 核心管理层 (Key Personnel)

```entity:Person
id: "PER-PM-ZHANG"
supplier_id: "SUP-A"
name: "张三 (项目经理)"
id_card_last4: "1234"
roles: ["Project Manager"]
has_social_security: true
honors: ["优秀项目经理2023"]
```

```entity:Person
id: "PER-TD-LI"
supplier_id: "SUP-A"
name: "李四 (技术负责人)"
id_card_last4: "5678"
roles: ["Technical Director"]
has_social_security: true
```

## 技术骨干 (Core Members)

```entity:Person
id: "PER-CORE-01"
supplier_id: "SUP-A"
name: "王五"
roles: ["Backend Lead"]
```

```entity:Person
id: "PER-CORE-02"
supplier_id: "SUP-A"
name: "赵六"
roles: ["Frontend Lead"]
```

```entity:Person
id: "PER-CORE-03"
supplier_id: "SUP-A"
name: "钱七"
roles: ["DevOps"]
```

## 实施团队 (Team Members, 仅列举部分)

```entity:Person
id: "PER-TEAM-01"
name: "实施员A"
roles: ["Engineer"]
```
# ... 其他 9 人省略，但在实际系统中会全部列出
