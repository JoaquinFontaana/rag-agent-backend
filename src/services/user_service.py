from src.models.entities.User import User
from src.models.entities.Role import RoleEnum, Role
from src.dtos.user import UserCreate
from src.db import engine
from sqlmodel import Session, select
from fastapi import HTTPException
from src.security.hash import hash_password
class UserService:

    def create_user(self,user_data:UserCreate):
        if self.exist_by_email(user_data.email):
            raise HTTPException(status_code=400,detail="The email already exists")
        role = self.find_role_by_name(RoleEnum.USER.value)
        
        if role.id is None:
            raise HTTPException(status_code=500, detail="Role ID not found")
        
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            role_id=role.id
        )    
        self.save(user)
         
        
    def save(self,user:User):
        with Session(engine) as session:
            session.add(user)
            session.commit()

    def find_by_id(self,id:int) -> User:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.id == id)).first()
            if not user:
                raise HTTPException(status_code=404,detail="The user doesnt exists")
            # Access role to load it before session closes
            _ = user.role
        return user
    
    def find_by_email(self,email:str) -> User:
        with Session(engine) as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if not user:
                raise HTTPException(status_code=404,detail="The user doesnt exists")
            # Access role to load it before session closes
            _ = user.role
        return user

    def exist_by_email(self, email: str) -> bool:
        with Session(engine) as session:
            return session.exec(select(User).where(User.email == email)).first() is not None

    def find_role_by_name(self,name:str) -> Role:
        with Session(engine) as session:
            role = session.exec(select(Role).where(Role.name == name)).first()
            if not role:
                raise HTTPException(status_code=404,detail=f"The role {name} doesnt exist")
        return role