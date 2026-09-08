from decimal import Decimal

from app.domain.enums import PerfilUsuario
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import Estoque, Produto, Unidade, Usuario
from app.infrastructure.security import gerar_hash_senha


def executar_seed():
    db = SessionLocal()

    try:
        gerente = (
            db.query(Usuario)
            .filter(Usuario.email == "gerente@empresa.com.br")
            .first()
        )

        if gerente is None:
            gerente = Usuario(
                nome="Gerente",
                email="gerente@empresa.com.br",
                senha_hash=gerar_hash_senha("123456"),
                perfil=PerfilUsuario.GERENTE,
            )

            db.add(gerente)
            db.flush()

            print("Gerente criado com sucesso.")
        else:
            print("Gerente ja existe.")

        unidade = (
            db.query(Unidade)
            .filter(Unidade.nome == "Raízes do Nordeste - Campinas")
            .first()
        )

        if unidade is None:
            unidade = Unidade(
                nome="Raízes do Nordeste - Campinas",
                endereco="Rua Principal, 100",
                cidade="Campinas",
            )

            db.add(unidade)
            db.flush()

            print("Unidade criada com sucesso.")
        else:
            print("Unidade ja existe.")

        produto = (
            db.query(Produto)
            .filter(Produto.nome == "Baião de Dois")
            .first()
        )

        if produto is None:
            produto = Produto(
                nome="Baião de Dois",
                descricao="Baião de dois tradicional",
                preco=Decimal("29.90"),
            )

            db.add(produto)
            db.flush()

            print("Produto criado com sucesso.")
        else:
            print("Produto ja existe.")

        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.unidade_id == unidade.id,
                Estoque.produto_id == produto.id,
            )
            .first()
        )

        if estoque is None:
            estoque = Estoque(
                unidade_id=unidade.id,
                produto_id=produto.id,
                quantidade=10,
            )

            db.add(estoque)

            print("Estoque criado com sucesso.")
        else:
            print("Estoque ja existe.")

        db.commit()

        print("Seed finalizado com sucesso.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    executar_seed()