from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    id: int
    fullname: str
    email: str
    phone: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
