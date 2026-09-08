from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.errors import (
    ErroResposta,
    ErroValidacaoResposta,
)
from app.application.permissions import exigir_gerente
from app.application.schemas import ProdutoCriacao, ProdutoResposta
from app.infrastructure.database import get_db
from app.infrastructure.models import Produto, Usuario


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
)


@router.post(
    "",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {
            "model": ErroResposta,
            "description": "Não autenticado ou token inválido",
        },
        403: {
            "model": ErroResposta,
            "description": "Acesso permitido apenas para gerente",
        },
        422: {
            "model": ErroValidacaoResposta,
            "description": "Erro de validação dos dados enviados",
        },
    },
)
def criar_produto(
    dados: ProdutoCriacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    produto = Produto(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
    )

    db.add(produto)
    db.commit()
    db.refresh(produto)

    return produto


@router.get(
    "",
    response_model=list[ProdutoResposta],
    responses={
        401: {
            "model": ErroResposta,
            "description": "Não autenticado ou token inválido",
        },
    },
)
def listar_produtos(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return db.query(Produto).all()