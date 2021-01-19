import pymysql
import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, create_engine, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker

from settings import DB_URL


class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    __mapper_args__ = {"always_refresh": True}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_on = Column(DateTime, server_default=func.now(), server_onupdate=func.now())


pymysql.install_as_MySQLdb()
engine: sqlalchemy.engine.base.Engine = create_engine(DB_URL, pool_recycle=3600)
session: sqlalchemy.orm.session.sessionmaker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
base = declarative_base(cls=Base)
