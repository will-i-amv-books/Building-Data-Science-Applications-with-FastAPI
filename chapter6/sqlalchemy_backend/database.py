import sqlalchemy as sa
from databases import Database


DATABASE_URL = "sqlite:///chapter6_sqlalchemy.db"
database = Database(DATABASE_URL)
sqlalchemy_engine = sa.create_engine(DATABASE_URL)


def get_database() -> Database:
    return database
