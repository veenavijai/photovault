from pydantic import BaseModel

class UserInfo(BaseModel):
    email: str
    device_id: str

class SessionInfo(BaseModel):
    device_id: str
    code: int

class FileInfo(BaseModel):
    file_name: str