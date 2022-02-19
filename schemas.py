from datetime import datetime
from typing import List
from pydantic import BaseModel, BaseSettings


class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_NAME: str

    SECRET_KEY: str

    class Config:
        env_file = ".env"



class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    is_active: bool = True

    class Config:
        orm_mode = True


class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool

    class Config:
        orm_mode = True


class User(UserBase):
    id: int

    class Config:
        orm_mode = True



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None



class InflowBase(BaseModel):
    date: datetime = datetime.now()
    description: str = 'Прочие доходы'
    sum: int = 0


class InflowCreate(InflowBase):
    class Config:
        orm_mode = True


class InflowInDB(InflowBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class InflowUser(BaseModel):
    inflow: List[InflowInDB] = []

    class Config:
        orm_mode = True



class OutflowBase(BaseModel):
    date: datetime = datetime.now()
    description: str = 'Прочие расходы'
    sum: int = 0


class OutflowCreate(OutflowBase):
    class Config:
        orm_mode = True


class OutflowInDB(OutflowBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class OutflowUser(BaseModel):
    outflow: List[OutflowInDB] = []

    class Config:
        orm_mode = True



class OutflowRegularBase(BaseModel):
    description: str = 'Ежемесячные расходы'
    sum: int = 0


class OutflowRegularCreate(OutflowRegularBase):
    class Config:
        orm_mode = True


class OutflowRegularInDB(OutflowRegularBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class OutflowRegularUser(BaseModel):
    outflow_regular: List[OutflowRegularInDB] = []

    class Config:
        orm_mode = True
