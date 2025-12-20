from pydantic import BaseModel

class MathConfig(BaseModel):
    precision: int
    mode: str
