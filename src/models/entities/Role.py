from enum import Enum
from sqlmodel import SQLModel, Field
class RoleEnum(Enum):
    USER = "user"
    ADMIN = "admin"

class Role(SQLModel, table=True):
    id: int | None = Field(primary_key=True,default=None)
    name:str = Field(unique=True)

