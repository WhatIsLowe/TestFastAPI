import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from envparse import env
env.read_envfile()

engine_pg = create_engine(
    "postgresql://{user}:{password}@{host}:{port}/{database}".format(
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASS'],
        host=os.environ['POSTGRES_HOST'],
        port=os.environ['POSTGRES_PORT'],
        database=os.environ['POSTGRES_DB'],
    ),
    pool_size=4,
    max_overflow=0,
    pool_recycle=300,
    pool_timeout=120,
    connect_args={"connect_timeout": 20},
)
SessionLocalPG = sessionmaker(autocommit=False, autoflush=False, bind=engine_pg)

BasePG = declarative_base()
