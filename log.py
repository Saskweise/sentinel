from pydantic import BaseModel
from datetime import datetime 

class Log(BaseModel):
    ip: str
    request: str
    route: str
    timestamp: datetime
    code_response: int
