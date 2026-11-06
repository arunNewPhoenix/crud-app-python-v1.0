from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    item: str = Field(min_length=1, max_length=160)
    quantity: int = Field(gt=0, le=10000)
    unit_price: float = Field(gt=0, le=10000000)


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_name: str
    item: str
    quantity: int
    unit_price: float
    status: str
    created_at: datetime
