# models.td

```model: ProjectTask
class ProjectTask(BaseModel):
    name: str
    due_date: datetime.date # 我们可以使用 datetime，因为它在 config.td 中被导出了
    priority: str = "medium"
```
