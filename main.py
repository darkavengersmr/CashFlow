from datetime import datetime, timedelta

from database import database, engine, metadata
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

import crud
import schemas

from config import SECRET_KEY


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "register",
        "description": "Регистрация новых пользователей",
    },
    {
        "name": "token",
        "description": "Обновление токенов доступа",
    },
    {
        "name": "user",
        "description": "Получение данных из профиля пользователя",
    },
    {
        "name": "inflow",
        "description": "Доходы",
    },
    {
        "name": "outflow",
        "description": "Расходы",
    },
    {
        "name": "outflow regular",
        "description": "Регулярные расходы",
    },
    {
        "name": "assets",
        "description": "Активы",
    },
    {
        "name": "liabilities",
        "description": "Пассивы",
    },
]

app = FastAPI(
    title="Cashflow Api",
    version="1.0.0",
    openapi_tags=tags_metadata,
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    #print(get_password_hash(plain_password))
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(username: str):
    user = await crud.get_user_by_username(username)
    if user:
        return schemas.UserInDB(**user)


async def authenticate_user(username: str, password: str):
    user = await crud.get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def is_user(user_id: int, current_user):
    db_user = await crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user['email'] != current_user.email:
        raise HTTPException(status_code=404, detail="Query for other user prohibited")
    return db_user


@app.post("/register", response_model=schemas.User, tags=["register"])
async def create_user(user: schemas.UserCreate):
    db_user = await crud.get_user_by_email(email=user.email)
    hashed_password: str = get_password_hash(user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(user=user, hashed_password=hashed_password)


@app.post("/token", response_model=schemas.Token , tags=["token"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user", response_model=schemas.User, tags=["user"])
async def read_user(current_user: schemas.User = Depends(get_current_active_user)):
    return await is_user(current_user.id, current_user)


@app.get("/users/{user_id}/inflow/", response_model=schemas.InflowUser, tags=["inflow"])
async def get_inflow_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.get_inflow_user(user_id=user_id)


@app.post("/users/{user_id}/inflow/", response_model=schemas.InflowInDB, tags=["inflow"])
async def create_inflow_for_user(user_id: int, inflow: schemas.InflowCreate,
                                 current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.create_user_inflow(inflow=inflow, user_id=user_id)


@app.delete("/users/{user_id}/inflow/", tags=["inflow"])
async def delete_inflow_for_user(user_id: int, inflow_id: int,
                                 current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.delete_inflow_user(inflow_id=inflow_id, user_id=user_id)


@app.get("/users/{user_id}/outflow/", response_model=schemas.OutflowUser, tags=["outflow"])
async def get_outflow_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.get_outflow_user(user_id=user_id)


@app.post("/users/{user_id}/outflow/", response_model=schemas.OutflowInDB, tags=["outflow"])
async def create_outflow_for_user(user_id: int, outflow: schemas.OutflowCreate,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.create_user_outflow(outflow=outflow, user_id=user_id)


@app.delete("/users/{user_id}/outflow/", tags=["outflow"])
async def delete_outflow_for_user(user_id: int, outflow_id: int,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.delete_outflow_user(outflow_id=outflow_id, user_id=user_id)


@app.get("/users/{user_id}/outflow_regular/", response_model=schemas.OutflowRegularUser, tags=["outflow regular"])
async def get_outflow_regular_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.get_outflow_regular_user(user_id=user_id)


@app.post("/users/{user_id}/outflow_regular/", response_model=schemas.OutflowRegularInDB, tags=["outflow regular"])
async def create_outflow_regular_for_user(user_id: int, outflow_regular: schemas.OutflowRegularCreate,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.create_user_outflow_regular(outflow_regular=outflow_regular, user_id=user_id)


@app.put("/users/{user_id}/outflow_regular/", tags=["outflow regular"])
async def create_outflow_regular_for_user(user_id: int, outflow_regular: schemas.OutflowRegularOut,
                                          current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.update_user_outflow_regular(outflow_regular=outflow_regular, user_id=user_id)


@app.delete("/users/{user_id}/outflow_regular/", tags=["outflow regular"])
async def delete_outflow_regular_for_user(user_id: int, outflow_regular_id: int,
                                          current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.delete_outflow_regular_user(outflow_regular_id=outflow_regular_id, user_id=user_id)


@app.post("/users/{user_id}/assets/", response_model=schemas.AssetInDB, tags=["assets"])
async def create_asset_for_user(user_id: int, asset: schemas.AssetCreate,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.create_user_asset(asset=asset, user_id=user_id)


@app.get("/users/{user_id}/assets/", response_model=schemas.AssetUser, tags=["assets"])
async def get_assets_for_user(user_id: int, date: datetime = datetime.now(),
                              current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.get_assets_user(user_id=user_id, date=date)


@app.put("/users/{user_id}/assets/", tags=["assets"])
async def update_asset_for_user(user_id: int, asset: schemas.AssetOut,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.update_user_asset(asset=asset, user_id=user_id)


@app.delete("/users/{user_id}/assets/", tags=["assets"])
async def delete_asset_for_user(user_id: int, asset: schemas.AssetDelete,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.update_user_asset(asset=asset, user_id=user_id)


@app.post("/users/{user_id}/liabilities/", response_model=schemas.LiabilitieInDB, tags=["liabilities"])
async def create_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieCreate,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.create_user_liabilitie(liabilitie=liabilitie, user_id=user_id)


@app.get("/users/{user_id}/liabilities/", response_model=schemas.LiabilitieUser, tags=["liabilities"])
async def get_liabilities_for_user(user_id: int, date: datetime = datetime.now(),
                                   current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.get_liabilities_user(user_id=user_id, date=date)


@app.put("/users/{user_id}/liabilities/", tags=["liabilities"])
async def update_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieOut,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.update_user_liabilitie(liabilitie=liabilitie, user_id=user_id)


@app.delete("/users/{user_id}/liabilities/", tags=["liabilities"])
async def delete_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieDelete,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user)
    return await crud.update_user_liabilitie(liabilitie=liabilitie, user_id=user_id)