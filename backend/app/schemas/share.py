from pydantic import BaseModel
from typing import Optional

class ShareRequest(BaseModel):
    email: str
