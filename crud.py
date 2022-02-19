from datetime import datetime, timedelta

from database import database
from sqlalchemy import and_
from models import users, inflows, outflows, outflows_regular, assets, liabilities
import schemas


async def get_user(user_id: int):
    result = await database.fetch_one(users.select().where(users.c.id == user_id))
    if result:
        return dict(result)
    else:
        return None


async def get_user_by_email(email: str):
    return await database.fetch_one(users.select().where(users.c.email == email))


async def get_user_by_username(username: str):
    return await database.fetch_one(users.select().where(users.c.username == username))


async def get_users(skip: int = 0, limit: int = 100):
     results = await database.fetch_all(users.select().offset(skip).limit(limit))
     return [dict(result) for result in results]


async def create_user(user: schemas.UserCreate, hashed_password: str):
    db_user = users.insert().values(username=user.username, email=user.email, hashed_password=hashed_password, is_active=user.is_active)
    user_id = await database.execute(db_user)
    return schemas.User(**user.dict(), id=user_id)


async def create_user_inflow(inflow: schemas.InflowCreate, user_id: int):
    query = inflows.insert().values(**inflow.dict(), owner_id=user_id)
    inflow_id = await database.execute(query)
    return schemas.InflowInDB(**inflow.dict(), id=inflow_id, owner_id=user_id)


async def get_inflow_user(user_id: int, date_in: datetime, date_out: datetime):
    result = dict()
    list_inflows = await database.fetch_all(inflows.select().where(and_(inflows.c.owner_id == user_id,
                                                                        inflows.c.date >= date_in,
                                                                        inflows.c.date <= date_out)))
    result.update({"inflow": [dict(result) for result in list_inflows]})
    return result


async def delete_inflow_user(inflow_id: int, user_id: int):
    query = inflows.select().where(and_(inflows.c.id == inflow_id, inflows.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = inflows.delete().where(and_(inflows.c.id == inflow_id, inflows.c.owner_id == user_id))
        await database.execute(query)
        result = {"result": "inflow deleted"}
    else:
        result = {"result": "inflow for delete not found"}
    return result


async def create_user_outflow(outflow: schemas.OutflowCreate, user_id: int):
    query = outflows.insert().values(**outflow.dict(), owner_id=user_id)
    outflow_id = await database.execute(query)
    return schemas.OutflowInDB(**outflow.dict(), id=outflow_id, owner_id=user_id)


async def get_outflow_user(user_id: int, date_in: datetime, date_out: datetime):
    result = dict()
    list_outflows = await database.fetch_all(outflows.select().where(and_(inflows.c.owner_id == user_id,
                                                                     inflows.c.date >= date_in,
                                                                     inflows.c.date <= date_out)))
    result.update({"outflow": [dict(result) for result in list_outflows]})
    return result


async def delete_outflow_user(outflow_id: int, user_id: int):
    query = outflows.select().where(and_(outflows.c.id == outflow_id, inflows.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = outflows.delete().where(and_(outflows.c.id == outflow_id, inflows.c.owner_id == user_id))
        await database.execute(query)
        result = {"result": "outflow deleted"}
    else:
        result = {"result": "outflow for delete not found"}
    return result


async def create_user_outflow_regular(outflow_regular: schemas.OutflowRegularCreate, user_id: int):
    query = outflows_regular.insert().values(**outflow_regular.dict(), owner_id=user_id)
    outflow_regular_id = await database.execute(query)
    return schemas.OutflowRegularInDB(**outflow_regular.dict(), id=outflow_regular_id, owner_id=user_id)


async def get_outflow_regular_user(user_id: int):
    result = dict()
    list_outflows_regular = await database.fetch_all(
        outflows_regular.select().where(outflows_regular.c.owner_id == user_id))
    result.update({"outflow_regular": [dict(result) for result in list_outflows_regular]})
    return result


async def update_user_outflow_regular(user_id: int, outflow_regular: schemas.OutflowRegularOut):
    query = outflows_regular.select().where(and_(outflows_regular.c.id == outflow_regular.id,
                                                 outflows_regular.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = outflows_regular.update().where(
            and_(outflows_regular.c.id == outflow_regular.id, outflows_regular.c.owner_id == user_id)).values(
            description=outflow_regular.description, sum=outflow_regular.sum)
        await database.execute(query)
        result = {"result": "outflow regular updated"}
    else:
        result = {"result": "outflow regular for update not found"}
    return result


async def delete_outflow_regular_user(outflow_regular_id: int, user_id: int):
    query = outflows_regular.select().where(and_(outflows_regular.c.id == outflow_regular_id,
                                                 outflows_regular.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = outflows_regular.delete().where(and_(outflows_regular.c.id == outflow_regular_id,
                                                outflows_regular.c.owner_id == user_id))
        await database.execute(query)
        result = {"result": "regular outflow deleted"}
    else:
        result = {"result": "regular outflow for delete not found"}
    return result


async def create_user_asset(asset: schemas.AssetCreate, user_id: int):
    query = assets.insert().values(**asset.dict(), owner_id=user_id)
    asset_id = await database.execute(query)
    return schemas.AssetInDB(**asset.dict(), id=asset_id, owner_id=user_id)


async def get_assets_user(user_id: int, date: datetime):
    result = dict()
    list_assets = await database.fetch_all(assets.select().where(and_(assets.c.owner_id == user_id,
                                                                 assets.c.date_in <= date,
                                                                 date <= assets.c.date_out)))
    result.update({"assets": [dict(result) for result in list_assets]})
    return result


async def update_user_asset(asset: schemas.AssetOut, user_id: int):
    query = assets.select().where(and_(assets.c.id == asset.id, assets.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = assets.update().where(and_(assets.c.id == asset.id, assets.c.owner_id == user_id)).values(
            date_out=datetime.now())
        await database.execute(query)
        if hasattr(asset, 'sum') and asset.sum > 0:
            query = assets.insert().values(date_in=datetime.now(), date_out=datetime.now() + timedelta(days=100000),
                                           description=asset.description, sum=asset.sum, owner_id=user_id)
            await database.execute(query)
            result = {"result": "asset updated"}
        else:
            result = {"result": "asset deleted"}
    else:
        result = {"result": "asset for update/delete not found"}
    return result


async def create_user_liabilitie(liabilitie: schemas.LiabilitieCreate, user_id: int):
    query = liabilities.insert().values(**liabilitie.dict(), owner_id=user_id)
    liabilitie_id = await database.execute(query)
    return schemas.LiabilitieInDB(**liabilitie.dict(), id=liabilitie_id, owner_id=user_id)


async def get_liabilities_user(user_id: int, date: datetime):
    result = dict()
    list_liabilities = await database.fetch_all(liabilities.select().where(and_(liabilities.c.owner_id == user_id,
                                                                                liabilities.c.date_in <= date,
                                                                                date <= liabilities.c.date_out)))
    result.update({"liabilities": [dict(result) for result in list_liabilities]})
    return result


async def update_user_liabilitie(liabilitie: schemas.LiabilitieOut, user_id: int):
    query = liabilities.select().where(and_(liabilities.c.id == liabilitie.id, liabilities.c.owner_id == user_id))
    result = await database.execute(query)
    if result:
        query = liabilities.update().where(
            and_(liabilities.c.id == liabilitie.id, liabilities.c.owner_id == user_id)).values(date_out=datetime.now())
        await database.execute(query)
        if hasattr(liabilitie, 'sum') and liabilitie.sum > 0:
            query = liabilities.insert().values(date_in=datetime.now(),
                                                date_out=datetime.now() + timedelta(days=100000),
                                                description=liabilitie.description,
                                                sum=liabilitie.sum,
                                                owner_id=user_id)
            await database.execute(query)
            result = {"result": "liabilitie updated"}
        else:
            result = {"result": "liabilitie deleted"}
    else:
        result = {"result": "liabilitie for update/delete not found"}
    return result