# 形式与资格审查表 - 专家李 (供应商 A)

> **指令**: 请核对实物及资质原件。如有任意一项 "CRITICAL" 未通过，请勾选 `is_knockout` 并说明理由。

```config:python
from use_cases.bid_agent.models.review import ReviewResultEntry
```

## 形式审查 (一票否决)

```entity:ReviewResultEntry
expert_id: "EXPERT-LI"
response_item_id: "REQ-PHY-01" # 密封检查
is_passed: true
comment: "密封完好，骑缝章完整。"
```

```entity:ReviewResultEntry
expert_id: "EXPERT-LI"
response_item_id: "REQ-PHY-02" # 份数检查
is_passed: true
```

## 资格审查

```entity:ReviewResultEntry
expert_id: "EXPERT-LI"
response_item_id: "REQ-QUAL-02" # ISO9001
is_passed: true
comment: "原件核对无误，在有效期内。"
```
