from database import database
from sqlalchemy import and_
from models import users, inflows, outflows, outflows_regular
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


# async def get_inflow(skip: int = 0, limit: int = 100):
#     query = inflows.select().offset(skip).limit(limit)
#     results = await database.fetch_all(query)
#     return [dict(result) for result in results]


async def create_user_inflow(inflow: schemas.InflowCreate, user_id: int):
    query = inflows.insert().values(**inflow.dict(), owner_id=user_id)
    inflow_id = await database.execute(query)
    return schemas.InflowInDB(**inflow.dict(), id=inflow_id, owner_id=user_id)


async def get_inflow_user(user_id: int):
    result = dict()
    list_inflows = await database.fetch_all(inflows.select().where(inflows.c.owner_id == user_id))
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
        result = {"result": "inflow to delete not found"}
    return result


async def create_user_outflow(outflow: schemas.OutflowCreate, user_id: int):
    query = outflows.insert().values(**outflow.dict(), owner_id=user_id)
    outflow_id = await database.execute(query)
    return schemas.OutflowInDB(**outflow.dict(), id=outflow_id, owner_id=user_id)


async def get_outflow_user(user_id: int):
    result = dict()
    list_outflows = await database.fetch_all(outflows.select().where(outflows.c.owner_id == user_id))
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
        result = {"result": "outflow to delete not found"}
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
        result = {"result": "regular outflow to delete not found"}
    return result
