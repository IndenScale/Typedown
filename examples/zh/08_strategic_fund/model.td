# 1. 核心模型定义 (Core Models)

定义资金、人员和项目的数据结构。


```model: Domain
from enum import Enum

class Domain(str, Enum):
    AI = "Artificial Intelligence"
    BIO = "Biotechnology"
    QUANTUM = "Quantum Computing"
    NEW_ENERGY = "New Energy"
    SEMICONDUCTOR = "Semiconductor"
```

```model: Fund
class Fund(BaseModel):
    name: str
    year: int
    total_budget_cny: float
    description: str
    priority_domains: List[Domain]
```

```model: Specialist
class Specialist(BaseModel):
    name: str # e.g. "user-zhang-san"
    title: str # "Professor", "Engineer"
    degrees: List[str] # ["PhD", "Master"]
    bad_records: int # 0 means clean
    research_domains: List[Domain]
```


```model: Milestone
class Milestone(BaseModel):
    date: str
    goal: str
    deliverables: List[str]
```

```model: BudgetItem
class BudgetItem(BaseModel):
    category: str # "Equipment", "Personnel", "Travel", "Outsourcing"
    amount: float
    justification: str
```

```model: ResearchPlan
class ResearchPlan(BaseModel):
    abstract: str
    background: str
    objectives: List[str]
    methodology_steps: List[str]
    technical_challenges: List[str]
    milestones: List[Milestone]
    budget_breakdown: List[BudgetItem]
    team_members: List[str] # List of names
```

```model: ProjectApplication
class ProjectApplication(BaseModel):
    title: str
    applicant_id: str # Link to Specialist
    domain: Domain
    requested_budget_cny: float
    status: str # "Draft", "Submitted", "Approved", "Archived"
    plan: ResearchPlan
    
    @field_validator('requested_budget_cny')
    def check_budget_limit(cls, v):
        if v > 50000000.0:
            raise ValueError('Single project budget cannot exceed 50M CNY')
        return v
```


