```entity Skill
name: "browser_action"
description: "控制无头浏览器与网页进行交互。"
version: "1.2.0"
author: "AgentOps Team"

parameters:
  - name: "action"
    type: "enum[click, type, scroll]"
    description: "要在页面上执行的动作。"
    required: true
  - name: "selector"
    type: "css_selector"
    description: "目标元素的 CSS 选择器。"
    required: true
  - name: "value"
    type: "string"
    description: "要输入的文本 (仅当 action 为 'type' 时需要)。"
    required: false

guidelines:
  - "在点击之前，始终等待网络处于空闲状态 (network idle)。"
  - "如果未找到选择器，请截屏以供调试。"
  - "未经用户明确确认，切勿提交表单。"

examples:
  - description: "在 Google 上搜索 Typedown"
    code: |
      {
        "action": "type",
        "selector": "input[name='q']",
        "value": "Typedown consensus modeling"
      }
```

```spec
# 确保技能定义的质量
def check_parameter_quality(skill: Skill):
    for param in skill.parameters:
        # 强制要求每个参数都有足够详细的描述
        assert len(param.description) > 10, f"参数 '{param.name}' 的描述太短了。"

        # 强制要求严格的类型定义
        if param.required:
            assert param.type != "any", f"必填参数 '{param.name}' 的类型不能是 'any'。"
```
