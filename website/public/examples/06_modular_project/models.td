# models.td

```model: ProjectTask
class ProjectTask(BaseModel):
    name: str
    due_date: datetime.date # We can use datetime because it was exported in config.td
    priority: str = "medium"
```
