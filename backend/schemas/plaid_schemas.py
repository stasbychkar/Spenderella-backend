from pydantic import BaseModel
from typing import Optional

class TokenModel(BaseModel):
    public_token: str
    institution_name: str

class AccessModel(BaseModel):
    access_token: str

class SyncRequestModel(BaseModel):
    access_token: str
    cursor: Optional[str] = None

class UpdateCategoryRequest(BaseModel):
    transaction_id: int
    new_category: str