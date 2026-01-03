```model:Skill
from typing import List, Dict, Optional
from pydantic import BaseModel, HttpUrl

class Example(BaseModel):
    description: str
    code: str

class Parameter(BaseModel):
    name: str
    type: str  # 例如: "string", "int"
    description: str
    required: bool = True

class Skill(BaseModel):
    """
    定义 Agent 可以拥有的能力 (Skill / Tool)。
    """
    name: str # 技能的唯一标识符
    description: str # 给 LLM 看的功能描述
    version: str = "1.0.0"
    author: str # 负责人

    # 供 LLM 调用的接口定义
    parameters: List[Parameter]

    # 严格的执行准则 (Guidelines)，用于减少幻觉
    guidelines: List[str]

    # Few-shot 示例，用于预热 Context
    examples: List[Example]
```

```config
export Skill
export Parameter
export Example
```
