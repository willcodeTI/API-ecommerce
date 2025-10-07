from database import Session, base, db
from models.produto import Produto

def inicializar_dados():        
    print("Inicializando dados...")
    try:
        with Session(bind=db) as session:
            if session.query(Produto).count() == 0:
                produtos_iniciais = [
                    Produto(nome="Notebook", preco=3500, estoque=50, descricao="Notebook gamer"),
                    Produto(nome="mouse", preco=85, estoque=100, descricao="mouse gamer sem fio RGB"),
                    Produto(nome="mouse pad", preco=30.0, estoque=300, descricao="mouse pad costurado e com led"),
                ]
                session.add_all(produtos_iniciais)
                session.commit()
                
    except Exception as e:
        print(f"Erro ao inicializar dados: {e}")
        base.metadata.create_all(bind=db) #criando todas as tabelas do banco de dados


if __name__ == "__main__":
    inicializar_dados()