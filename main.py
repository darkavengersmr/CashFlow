#!/usr/bin/python3

import uvicorn

from datetime import datetime, timedelta
import calendar

from typing import Optional

from database import database, engine, metadata
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from jose import JWTError, jwt
from passlib.context import CryptContext

import crud
import schemas

from config import SECRET_KEY, MY_INVITE


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 181 * 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Register",
        "description": "Регистрация новых пользователей",
    },
    {
        "name": "Token",
        "description": "Обновление токенов доступа",
    },
    {
        "name": "User",
        "description": "Получение данных из профиля пользователя",
    },
    {
        "name": "Inflow",
        "description": "Доходы",
    },
    {
        "name": "Inflow regular",
        "description": "Регулярные доходы",
    },
    {
        "name": "Outflow",
        "description": "Расходы",
    },
    {
        "name": "Outflow regular",
        "description": "Регулярные расходы",
    },
    {
        "name": "Assets",
        "description": "Активы",
    },
    {
        "name": "Liabilities",
        "description": "Пассивы",
    },
    {
        "name": "Categories",
        "description": "Категории активов и пассивов",
    },
    {
        "name": "Reports",
        "description": "Отчеты",
    },
    {
        "name": "Most polular",
        "description": "Самые популярные доходы/расходы (для подсказок)",
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


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
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


async def is_user(user_id: int, email: str):
    db_user = await crud.get_user(user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user['email'] != email:
        raise HTTPException(status_code=404, detail="Query for other user prohibited")
    return db_user


def month_begin():
    dt = datetime.now()
    return datetime.strptime(f"{dt.timetuple().tm_year}-{dt.timetuple().tm_mon}-01 00:00:00", "%Y-%m-%d %H:%M:%S")


def month_end():
    dt = datetime.now()
    _, num_days = calendar.monthrange(dt.timetuple().tm_year, dt.timetuple().tm_mon)
    return datetime.strptime(f"{dt.timetuple().tm_year}-{dt.timetuple().tm_mon}-{num_days} 23:59:59",
                             "%Y-%m-%d %H:%M:%S")


@app.get("/inflow")
async def redirect_inflow():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/outflow")
async def redirect_outflow():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/assets")
async def redirect_assets():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/liabilities")
async def redirect_liabilities():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/preferences")
async def redirect_preferences():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/login")
async def redirect_login():
    return RedirectResponse(url=f"/", status_code=303)


@app.get("/")
async def redirect_login():
    return RedirectResponse(url=f"/index.html", status_code=303)


@app.post("/register", response_model=schemas.User, tags=["Register"])
async def create_user(user: schemas.UserCreate):
    db_user = await crud.get_user_by_email(email=user.email)
    hashed_password: str = get_password_hash(user.password)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.invite != MY_INVITE:
        raise HTTPException(status_code=400, detail="Invite is broken")
    return await crud.create_user(user=user, hashed_password=hashed_password)


@app.post("/token", response_model=schemas.Token , tags=["Token"])
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


@app.get("/user", response_model=schemas.User, tags=["User"])
async def read_user(current_user: schemas.User = Depends(get_current_active_user)):
    return await is_user(current_user.id, current_user.email)


@app.get("/users/{user_id}/inflow/", response_model=schemas.InflowUser, tags=["Inflow"])
async def get_inflow_for_user(user_id: int, date_in: Optional[datetime] = month_begin(),
                              date_out: Optional[datetime] = month_end(),
                              current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_inflow_user(user_id=user_id, date_in=date_in, date_out=date_out)


@app.post("/users/{user_id}/inflow/", response_model=schemas.InflowInDB, tags=["Inflow"])
async def create_inflow_for_user(user_id: int, inflow: schemas.InflowCreate,
                                 current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_inflow(inflow=inflow, user_id=user_id)


@app.delete("/users/{user_id}/inflow/", tags=["Inflow"])
async def delete_inflow_for_user(user_id: int, inflow_id: int,
                                 current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.delete_inflow_user(inflow_id=inflow_id, user_id=user_id)


@app.get("/users/{user_id}/inflow_regular/", response_model=schemas.InflowRegularUser, tags=["Inflow regular"])
async def get_inflow_regular_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_inflow_regular_user(user_id=user_id)


@app.post("/users/{user_id}/inflow_regular/", response_model=schemas.InflowRegularInDB, tags=["Inflow regular"])
async def create_inflow_regular_for_user(user_id: int, inflow_regular: schemas.InflowRegularCreate,
                                         current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_inflow_regular(inflow_regular=inflow_regular, user_id=user_id)


@app.put("/users/{user_id}/inflow_regular/", tags=["Inflow regular"])
async def update_inflow_regular_for_user(user_id: int, inflow_regular: schemas.InflowRegularOut,
                                         current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_inflow_regular(inflow_regular=inflow_regular, user_id=user_id)


@app.delete("/users/{user_id}/inflow_regular/", tags=["Inflow regular"])
async def delete_inflow_regular_for_user(user_id: int, inflow_regular_id: int,
                                         current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.delete_inflow_regular_user(inflow_regular_id=inflow_regular_id, user_id=user_id)


@app.get("/users/{user_id}/outflow/", response_model=schemas.OutflowUser, tags=["Outflow"])
async def get_outflow_for_user(user_id: int, date_in: datetime = month_begin(), date_out: datetime = month_end(),
                               current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_outflow_user(user_id=user_id, date_in=date_in, date_out=date_out)


@app.post("/users/{user_id}/outflow/", response_model=schemas.OutflowInDB, tags=["Outflow"])
async def create_outflow_for_user(user_id: int, outflow: schemas.OutflowCreate,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_outflow(outflow=outflow, user_id=user_id)


@app.delete("/users/{user_id}/outflow/", tags=["Outflow"])
async def delete_outflow_for_user(user_id: int, outflow_id: int,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.delete_outflow_user(outflow_id=outflow_id, user_id=user_id)


@app.get("/users/{user_id}/outflow_regular/", response_model=schemas.OutflowRegularUser, tags=["Outflow regular"])
async def get_outflow_regular_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_outflow_regular_user(user_id=user_id)


@app.post("/users/{user_id}/outflow_regular/", response_model=schemas.OutflowRegularInDB, tags=["Outflow regular"])
async def create_outflow_regular_for_user(user_id: int, outflow_regular: schemas.OutflowRegularCreate,
                                  current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_outflow_regular(outflow_regular=outflow_regular, user_id=user_id)


@app.put("/users/{user_id}/outflow_regular/", tags=["Outflow regular"])
async def update_outflow_regular_for_user(user_id: int, outflow_regular: schemas.OutflowRegularOut,
                                          current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_outflow_regular(outflow_regular=outflow_regular, user_id=user_id)


@app.delete("/users/{user_id}/outflow_regular/", tags=["Outflow regular"])
async def delete_outflow_regular_for_user(user_id: int, outflow_regular_id: int,
                                          current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.delete_outflow_regular_user(outflow_regular_id=outflow_regular_id, user_id=user_id)


@app.post("/users/{user_id}/assets/", response_model=schemas.AssetInDB, tags=["Assets"])
async def create_asset_for_user(user_id: int, asset: schemas.AssetCreate,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_asset(asset=asset, user_id=user_id)


@app.get("/users/{user_id}/assets/", response_model=schemas.AssetUser, tags=["Assets"])
async def get_assets_for_user(user_id: int, date: datetime = datetime.now(),
                              current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_assets_user(user_id=user_id, date=date)


@app.put("/users/{user_id}/assets/", tags=["Assets"])
async def update_asset_for_user(user_id: int, asset: schemas.AssetOut,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_asset(asset=asset, user_id=user_id)


@app.delete("/users/{user_id}/assets/", tags=["Assets"])
async def delete_asset_for_user(user_id: int, asset: schemas.AssetDelete,
                                current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_asset(asset=asset, user_id=user_id)


@app.post("/users/{user_id}/liabilities/", response_model=schemas.LiabilitieInDB, tags=["Liabilities"])
async def create_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieCreate,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_liabilitie(liabilitie=liabilitie, user_id=user_id)


@app.get("/users/{user_id}/liabilities/", response_model=schemas.LiabilitieUser, tags=["Liabilities"])
async def get_liabilities_for_user(user_id: int, date: datetime = datetime.now(),
                                   current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_liabilities_user(user_id=user_id, date=date)


@app.put("/users/{user_id}/liabilities/", tags=["Liabilities"])
async def update_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieOut,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_liabilitie(liabilitie=liabilitie, user_id=user_id)


@app.delete("/users/{user_id}/liabilities/", tags=["Liabilities"])
async def delete_liabilitie_for_user(user_id: int, liabilitie: schemas.LiabilitieDelete,
                                     current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.update_user_liabilitie(liabilitie=liabilitie, user_id=user_id)


@app.get("/users/{user_id}/categories/", response_model=schemas.CategoryUser, tags=["Categories"])
async def get_categories_for_user(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_user_categories(user_id=user_id)


@app.post("/users/{user_id}/categories/", response_model=schemas.CategoryInDB, tags=["Categories"])
async def create_category_for_user(user_id: int, category: schemas.CategoryCreate,
                                   current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.create_user_category(category=category, user_id=user_id)


@app.delete("/users/{user_id}/categories/", tags=["Categories"])
async def delete_category_for_user(user_id: int, category_id: int,
                                   current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.delete_user_category(category_id=category_id, user_id=user_id)


@app.get("/users/{user_id}/reports/", response_model=schemas.ReportsUser, tags=["Reports"])
async def get_reports(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_reports(user_id=user_id)


@app.get("/users/{user_id}/export/", tags=["Reports"])
async def get_export(user_id: int, current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    await crud.get_export(user_id=user_id)
    return FileResponse(path=f'.\\static\\export\\cashflow{user_id}.xlsx', filename=f'cashflow{user_id}.xlsx',
                        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.get("/users/{user_id}/most_popular/", response_model=schemas.MostPopular, tags=["Most polular"])
async def get_most_popular(user_id: int, date_in: datetime = month_begin(), date_out: datetime = month_end(),
                           current_user: schemas.User = Depends(get_current_active_user)):
    await is_user(user_id, current_user.email)
    return await crud.get_most_popular(user_id=user_id, date_in=date_in, date_out=date_out)


app.mount("/", StaticFiles(directory="static"), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)