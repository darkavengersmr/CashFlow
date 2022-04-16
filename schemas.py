from datetime import datetime, timedelta
from typing import List, Union
from pydantic import BaseModel, BaseSettings



class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_NAME: str
    SECRET_KEY: str
    MY_INVITE: str

    class Config:
        env_file = ".env"


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str
    invite: str
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


class InflowRegularBase(BaseModel):
    description: str = 'Ежемесячные доходы'
    sum: int = 0


class InflowRegularCreate(InflowRegularBase):
    class Config:
        orm_mode = True


class InflowRegularInDB(InflowRegularBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class InflowRegularOut(BaseModel):
    id: int
    description: str
    sum: int


class InflowRegularUser(BaseModel):
    inflow_regular: List[InflowRegularInDB] = []

    class Config:
        orm_mode = True


class OutflowBase(BaseModel):
    date: datetime = datetime.now()
    description: str = 'Прочие расходы'
    sum: int = 0


class OutflowOut(BaseModel):
    description: str
    sum: int
    count: int


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


class OutflowRegularOut(BaseModel):
    id: int
    description: str
    sum: int


class OutflowRegularUser(BaseModel):
    outflow_regular: List[OutflowRegularInDB] = []

    class Config:
        orm_mode = True


class AssetBase(BaseModel):
    date_in: datetime = datetime.strptime(f"{datetime.now().timetuple().tm_year}-{datetime.now().timetuple().tm_mon}-"
                                          f"01 00:00:00", "%Y-%m-%d %H:%M:%S")
    date_out: datetime = datetime.now() + timedelta(days=100000)
    description: str = 'Прочие активы'
    sum: int = 0
    category_id: Union[int, None]


class AssetCreate(AssetBase):
    class Config:
        orm_mode = True


class AssetInDB(AssetBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class AssetOut(BaseModel):
    id: int
    description: str
    sum: int
    category_id: Union[int, None]

    class Config:
        orm_mode = True


class AssetDelete(BaseModel):
    id: int
    date: datetime = datetime.now()

    class Config:
        orm_mode = True


class AssetUser(BaseModel):
    assets: List[AssetOut] = []

    class Config:
        orm_mode = True


class LiabilitieBase(BaseModel):
    date_in: datetime = datetime.strptime(f"{datetime.now().timetuple().tm_year}-{datetime.now().timetuple().tm_mon}-"
                                          f"01 00:00:00", "%Y-%m-%d %H:%M:%S")
    date_out: datetime = datetime.now() + timedelta(days=100000)
    description: str = 'Прочие пассивы'
    sum: int = 0
    category_id: Union[int, None] = None


class LiabilitieCreate(LiabilitieBase):
    class Config:
        orm_mode = True


class LiabilitieInDB(LiabilitieBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class LiabilitieOut(BaseModel):
    id: int
    description: str
    sum: int
    category_id: Union[int, None]

    class Config:
        orm_mode = True


class LiabilitieDelete(BaseModel):
    id: int
    date: datetime = datetime.now()

    class Config:
        orm_mode = True


class LiabilitieUser(BaseModel):
    liabilities: List[LiabilitieOut] = []

    class Config:
        orm_mode = True


class CategoryBase(BaseModel):
    category: str = 'Прочая категория'


class CategoryCreate(CategoryBase):
    class Config:
        orm_mode = True


class CategoryInDB(CategoryBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class CategoryOut(BaseModel):
    id: int
    category: str

    class Config:
        orm_mode = True


class CategoryDelete(BaseModel):
    id: int

    class Config:
        orm_mode = True


class CategoryUser(BaseModel):
    categories: List[CategoryOut] = []

    class Config:
        orm_mode = True


class ReportsBase(BaseModel):
    description: str
    sum: int

class ReportsFlowBase(BaseModel):
    date: datetime
    description: str
    sum: int

class ReportsUser(BaseModel):
    assets: List[ReportsBase] = []
    liabilities: List[ReportsBase] = []
    inflow_regular: List[ReportsFlowBase] = []
    outflow_regular: List[ReportsFlowBase] = []

    class Config:
        orm_mode = True

class Popular(BaseModel):
    description: str
    sum: int

class MostPopular(BaseModel):
    most_popular: List[Popular] = []
    autocomplete: List = []

    class Config:
        orm_mode = True
