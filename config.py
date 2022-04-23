from starlette.config import Config
import schemas

config = Config(schemas.Settings.Config.env_file)

POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
POSTGRES_HOST = config('POSTGRES_HOST')
POSTGRES_PORT = config('POSTGRES_PORT', cast=int)
DATABASE_NAME = config('DATABASE_NAME')
MY_INVITE = config('MY_INVITE')
DEMO_USER_ID = config('DEMO_USER_ID', cast=int)

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = config('SECRET_KEY')

SQLALCHEMY_DATABASE_URL = \
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DATABASE_NAME}"

