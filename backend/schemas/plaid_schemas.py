from pydantic import BaseModel

class TokenModel(BaseModel):
    public_token: str
    institution_name: str

class AccessModel(BaseModel):
    access_token: str

class SyncRequestModel(BaseModel):
    item_id: str