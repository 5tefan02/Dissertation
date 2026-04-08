from sqlalchemy import Column, Integer, String, create_engine, DateTime, Date, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import URL


Base = declarative_base()


DB_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="1234", 
    host="localhost",
    port=5432,
    database="DB1"
)

engine = create_engine(DB_URL, echo=False, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)

Base.metadata.create_all(engine)
