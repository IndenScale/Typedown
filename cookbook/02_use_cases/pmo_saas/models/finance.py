from pydantic import BaseModel

class RegionalPolicy(BaseModel):
    region_code: str
    travel_allowance_per_day: float
    description: str
