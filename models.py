from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, DateTime
from database import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("username", String),
    Column("email", String, unique=True, index=True),
    Column("hashed_password", String),
    Column("is_active", Boolean, default=True)
)


inflows = Table(
    "inflow",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date", DateTime, nullable=False),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


inflows_regular = Table(
    "inflow_regular",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


outflows = Table(
    "outflow",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date", DateTime, nullable=False),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


outflows_regular = Table(
    "outflow_regular",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


assets = Table(
    "assets",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date_in", DateTime, nullable=False),
    Column("date_out", DateTime, nullable=False),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


liabilities = Table(
    "liabilities",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("date_in", DateTime, nullable=False),
    Column("date_out", DateTime, nullable=False),
    Column("description", String, nullable=False, default='unknown'),
    Column("sum", Integer, nullable=False, default=0),
    Column("owner_id", Integer, ForeignKey("users.id"))
)


categories = Table(
    "categories",
    metadata,
    Column("id", Integer, unique=True, primary_key=True, autoincrement=True),
    Column("category", String, nullable=False, default='unknown'),
    Column("owner_id", Integer, ForeignKey("users.id"))
)
