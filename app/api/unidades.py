from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.permissions import exigir_gerente
from app.application.schemas import (
    ProdutoResposta,
    UnidadeCriacao,
    UnidadeResposta,
)
from app.infrastructure.database import get_db
from app.infrastructure.models import Estoque, Produto, Unidade, Usuario


router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"],
)


@router.post(
    "",
    response_model=UnidadeResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_unidade(
    dados: UnidadeCriacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    unidade = Unidade(
        nome=dados.nome,
        endereco=dados.endereco,
        cidade=dados.cidade,
    )

    db.add(unidade)
    db.commit()
    db.refresh(unidade)

    return unidade


@router.get(
    "",
    response_model=list[UnidadeResposta],
)
def listar_unidades(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return db.query(Unidade).all()


@router.get(
    "/{unidade_id}/cardapio",
    response_model=list[ProdutoResposta],
)
def listar_cardapio(
    unidade_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    unidade = (
        db.query(Unidade)
        .filter(Unidade.id == unidade_id)
        .first()
    )

    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada",
        )

    produtos = (
        db.query(Produto)
        .join(Estoque, Produto.id == Estoque.produto_id)
        .filter(
            Estoque.unidade_id == unidade_id,
            Estoque.quantidade > 0,
            Produto.ativo.is_(True),
        )
        .all()
    )

    return produtos