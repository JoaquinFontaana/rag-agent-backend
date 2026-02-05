from typing import TypedDict
from datetime import datetime
class TokenPayload(TypedDict):
    sub:str #id
    exp:datetime
    iat:datetime
    role:str