from typing import Optional

from pydantic import BaseModel


class ShareRequest(BaseModel):
    email: str
