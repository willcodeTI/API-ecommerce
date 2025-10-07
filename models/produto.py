from database import base
from sqlalchemy import Column, Integer, String, Float, DateTime, func

#model SQLAlchemy para a tabela de produtos


class Produto(base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, nullable=False)
    descricao = Column(String)
    criado_em = Column(DateTime, server_default=func.current_timestamp())

# Definindo o que será exportado
__all__ = ["Produto"]