import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text, func #O create_engine cria seu banco de dados
from sqlalchemy.orm import sessionmaker, declarative_base
#configurando o banco de dados e dependências

db = create_engine(os.getenv("DATABASE_URL", 'sqlite:///ecommerce.db')) #criando o banco de dados
Session = sessionmaker(autocommit=False, autoflush=False, bind=db)

def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()

base = declarative_base() #criando a base do banco de dados

__all__ = ["get_db", "base", "db"]   
#base.metadata.create_all(bind=db) #criando todas as tabelas do banco de dados