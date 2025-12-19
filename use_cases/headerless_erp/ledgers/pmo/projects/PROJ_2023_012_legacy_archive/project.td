# 旧系统归档 (Legacy System Archival)

## 1. 时代的落幕

随着 Titan CRM 的上线，那台在地下室机房轰鸣了 20 年的 IBM AS/400 终于迎来了它的退休时刻。它见证了公司从一家只有 50 人的小作坊成长为跨国企业的全过程。

然而，断电并不意味着遗忘。根据美国 SEC 的要求以及《萨班斯-奥克斯利法案》(SOX)，所有的财务与交易历史数据必须保留至少 10 年，并且必须依然是“可读”的。

## 2. 项目核心定义

```config:python
import sys
import os
current_dir = os.getcwd()
erp_root = os.path.abspath(os.path.join(current_dir, "../../../../../.."))
if erp_root not in sys.path:
    sys.path.append(erp_root)

from use_cases.headerless_erp.models.pmo.project import Project
```

```entity:Project
id: "proj_2023_legacy_archive"
name: "Legacy System Archival"
code: "PROJ-2023-012"
manager_id: "emp_fin_head_001"
status: "Completed"
budget:
    amount: 200000
    currency: "USD"
```

## 3. 归档策略总结

我们最终放弃了物理磁带备份方案。虽然磁带便宜，但在长达 10 年的周期里，磁带机的维护和接口兼容性是一个巨大的隐形炸弹。

选型方案：**Amazon S3 Glacier Deep Archive**。
*   **成本**: 存储成本极低（$0.00099/GB/Month）。
*   **合规**: 启用了 Object Lock (Governance Mode)，确保数据在 10 年内不可被删除或篡改 (WORM)。
*   **模拟测试**: 我们在 2024 年 6 月进行了一次模拟审计数据抽取，用时 11 小时恢复了 2015 年的全年账目，符合预期。

本项目已于 2024 年 Q4 顺利结项。再见，AS/400。
