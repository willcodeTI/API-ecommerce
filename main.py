from sqlalchemy.exc import IntegrityError
from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Security 
from typing import List
from database import base, db, get_db
from sqlalchemy.orm import Session 
from database.seed import inicializar_dados #importando a função de inicialização de dados
from models.produto import Produto
from fastapi.security.api_key import APIKeyHeader
from schemas.produto import ProdutoCreate, Prodresponse, ProdAtualize
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
# Definindo a chave de API como uma constante

api_key_header = APIKeyHeader(name="X-API-Key")


async def lifespan_handler(app: FastAPI):
    base.metadata.create_all(bind=db)
    inicializar_dados()
    yield
    # Aqui você pode adicionar código para ser executado na finalização do aplicativo, se necessário




app = FastAPI(title="E-commerce API", version="1.0.0" , lifespan=lifespan_handler)




def verificar_autenticacao(api_key: str = Depends(api_key_header)):
    if api_key is None or api_key != API_KEY:
        raise HTTPException(status_code=401, detail="X-API-Key inválida ou ausente")
    print("Autenticação bem-sucedida")
    return True
   





@app.get("/ping")
async def read_root():
    return {"status": "ok",
             "message": "Api funcionando"}






@app.get("/produtos", response_model=List[Prodresponse])

async def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()

    return [Prodresponse.model_validate(p) for p in produtos]







@app.post("/produtos", status_code=201, response_model=dict)

async def criar_produto(produto: ProdutoCreate, db: Session = Depends(get_db),
                         _ : bool = Security(verificar_autenticacao)):
    
    if len(produto.nome.strip()) < 3:
        raise HTTPException(status_code=400, detail="Atenção! Nome do produto deve ter pelo menos 3 caracteres")

    if produto.estoque < 0:
        raise HTTPException(status_code=400, detail="Atenção! Estoque não pode ser negativo")
    
    if produto.preco <= 0:
        raise HTTPException(status_code=400, detail="Atenção! Preço deve ser maior que zero")
        
    try:
        novo_produto = Produto(**produto.model_dump())
        db.add(novo_produto)
        db.commit()
        db.refresh(novo_produto)
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro de integridade do banco de dados")
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
    produto_dict = Prodresponse.model_validate(novo_produto).model_dump()
    if produto_dict["criado_em"]:
        produto_dict["criado_em"] = produto_dict["criado_em"].isoformat()

    return JSONResponse(
        status_code=201, 
        content={
            "message": "Produto criado com sucesso",
            "produto": produto_dict
        }
    )






@app.get("/produtos/{produto_id}", response_model=Prodresponse) #esse endpoint retorna um produto específico com base no ID fornecido na URL.
async def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado, tente novamente usando outro ID")
    return Prodresponse.model_validate(produto)





@app.put("/produtos/{produto_id}", response_model=Prodresponse) #esse endpoint atualiza um produto específico com base no ID fornecido na URL.
async def atualizar_produto(produto_id: int, produto: ProdAtualize, db: Session = Depends(get_db), _: bool = Security(verificar_autenticacao)):
    produto_db = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto_db:
        raise HTTPException(status_code=404, detail="Produto não encontrado, tente novamente usando outro ID")

    for key, value in produto.model_dump().items():
        
        if key == "preco" and value is not None and value <= 0:
            raise HTTPException(status_code=400, detail="Preço inválido!! o preço deve ser maior que zero")

        if key == "estoque" and value is not None and value <= 0:
            raise HTTPException(status_code=400, detail="Estoque inválido!! o estoque não pode ser negativo")
               
        
        
        if key == "nome" and value is not None and len(value.strip()) < 3:
            raise HTTPException(status_code=400, detail="Nome inválido!! o nome do produto deve ter pelo menos 3 caracteres")
        
        
        if value is not None:
            setattr(produto_db, key, value)

    db.commit()
    db.refresh(produto_db)
    return Prodresponse.model_validate(produto_db)






@app.delete("/produtos/{produto_id}", status_code=204) #esse endpoint exclui um produto específico com base no ID fornecido na URL.
async def deletar_produto(produto_id: int,
                          db: Session = Depends(get_db),
                          _ : bool = Security(verificar_autenticacao)):
    produto_db = db.query(Produto).filter(Produto.id == produto_id).first()
    if produto_db is None:
        raise HTTPException(status_code=404, detail="Produto não encontrado, tente novamente usando outro ID")
    
    db.delete(produto_db)
    db.commit()
    return # Sem corpo na resposta




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))