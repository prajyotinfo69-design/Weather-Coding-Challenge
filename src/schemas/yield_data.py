from pydantic import BaseModel

class YieldOut(BaseModel):
    year: int
    total_yield: int

    class Config:
        from_attributes = True
