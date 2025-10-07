import pydantic as pd
from typing import Optional
from datetime import datetime


class ProdutoCreate(pd.BaseModel): #nome do produto, minimo 3 caracteres
    nome: str = pd.Field(..., min_length=3)
    preco: float = pd.Field(..., gt=0)
    estoque: int = pd.Field(..., ge=0)
    descricao: Optional[str] = None




class Prodresponse(pd.BaseModel):#resposta do produto
    id: int
    nome: str = pd.Field(..., min_length=3)
    preco: float = pd.Field(..., gt=0)
    estoque: int = pd.Field(..., ge=0)
    descricao: Optional[str] = None
    criado_em: datetime
    
    class Config:
        from_attributes = True #permite converter um objeto ORM em um modelo Pydantic



class ProdAtualize(pd.BaseModel): #atualização do produto
    nome: Optional[str] = None
    preco: Optional[float] = None
    estoque: Optional[int] = None
    descricao: Optional[str] = None