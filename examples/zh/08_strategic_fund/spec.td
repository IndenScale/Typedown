# 3. 全局业务规则 (Governance Specs)

这里定义了从"不可逾越的红线"。

```spec: governance_checks
@target(type="ProjectApplication", scope="global")
def governance_checks(subject):
    """
    Project Application Governance:
    1. Check Applicant Qualification (Must have PhD for > 5M projects).
    2. Check Applicant Track Record (No bad records).
    3. Check Fund Solvency (Total Approved + Current Request <= Fund Total).
    """
    # 0. Context Loading
    # In a real scenario, 'subject' is None for global scope, 
    # but here let's assume we are validating *all* ProjectApplications including the new one.
    # OR we bind to each ProjectApplication individually but need access to global Ledger.
    pass
```

```spec: check_individual_application
@target(type="ProjectApplication")
def check_individual_application(app):
    """对每个申请单的独立审查"""
    
    # 1. 资质审查 (Mock Lookup)
    # 在真实环境中，这里会查询 Ledger 或 数据库
    # 这里我们模拟一个查找逻辑
    
    specialists = sql(f"SELECT * FROM Specialist WHERE name = '{app.applicant_id}'")
    if not specialists:
        raise ValueError(f"申请人 '{app.applicant_id}' 不在专家库中！")
    
    applicant = specialists[0]
    

    # 规则：有不良记录的一票否决
    if applicant.bad_records > 0:
        raise ValueError(f"申请人 '{applicant.name}' 存在不良信用记录，申请驳回。")
        
    # 规则：项目领域必须在专家的研究领域内
    # Specialist.research_domains implies what they can do.
    # Note: domain is an Enum in model, stored as string in DB usually.
    # We check if the project domain is supported by the specialist.
    # Assuming exact match for simplicity.
    if app.domain not in applicant.research_domains:
        raise ValueError(f"专业领域不符：申请人 '{applicant.name}' 的研究领域 {applicant.research_domains} 不包含项目所需的 '{app.domain}'。")

    # 规则：重大项目(>1000万)需要博士学位
    if app.requested_budget_cny > 10000000.0:
        has_phd = any("PhD" in d for d in applicant.degrees)
        if not has_phd:
            raise ValueError(f"重大项目（>1000万）负责人必须拥有博士学位。'{applicant.name}' 资质不足。")

    # 2. 基金穿透审查 (Solvency Check)
    # 计算当前资金池水位
    funds = sql("SELECT * FROM Fund WHERE year = 2025")
    if not funds:
        return # No fund to check against
        
    fund = funds[0]
    
    # 获取所有已批准项目的总额
    approved_projects = sql("SELECT * FROM ProjectApplication WHERE status = 'Approved'")
    used_budget = sum(p.requested_budget_cny for p in approved_projects)
    
    # 加上当前申请的金额（如果它还不是Approved状态）
    projected_usage = used_budget
    if app.status != "Approved":
        projected_usage += app.requested_budget_cny
        
    remaining = fund.total_budget_cny - projected_usage
    
    if remaining < 0:
        raise ValueError(f"基金穿透风险！当前申请批准后将导致超支 {-remaining/10000:.2f} 万元。(基金池: {fund.total_budget_cny/10000:.0f}万, 预计使用: {projected_usage/10000:.0f}万)")

```spec: check_specialist_participation
@target(type="Specialist")
def check_specialist_participation(specialist):
    """
    研发人员活跃度检查：
    每一位在册专家必须至少参与过一个项目（无论是历史项目还是当前申请中）。
    """
    # 查询该专家名下的所有项目
    # 注意：sql 查询返回的是列表
    projects = sql(f"SELECT * FROM ProjectApplication WHERE applicant_id = '{specialist.name}'")
    
    if not projects:
        # 如果是新入职（比如 bad_records > 0 的可能被冻结，不再此列？暂不考虑复杂的排除逻辑）
        raise ValueError(f"人员闲置警告：专家 '{specialist.name}' 当前未参与任何项目（包括历史与在研）。请尽快指派项目或清理专家库。")
```

```
