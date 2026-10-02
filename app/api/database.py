"""Conexión a la base de datos.

Por defecto usa SQLite (ideal para tests y para correr sin Docker).
En Docker/Kubernetes se le pasa DATABASE_URL apuntando a Postgres, por ejemplo:
    postgresql+psycopg://tasks:tasks@db:5432/tasks
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tasks.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
