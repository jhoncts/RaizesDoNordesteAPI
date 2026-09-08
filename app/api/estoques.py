from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.permissions import exigir_gerente
from app.application.schemas import (
    EstoqueCriacao,
    EstoqueMovimentacao,
    EstoqueResposta,
)
from app.infrastructure.database import get_db
from app.infrastructure.models import Estoque, Produto, Unidade, Usuario


router = APIRouter(
    prefix="/estoques",
    tags=["Estoques"],
)


@router.post(
    "",
    response_model=EstoqueResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_estoque(
    dados: EstoqueCriacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    unidade = (
        db.query(Unidade)
        .filter(Unidade.id == dados.unidade_id)
        .first()
    )

    if unidade is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada",
        )

    produto = (
        db.query(Produto)
        .filter(Produto.id == dados.produto_id)
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )

    estoque_existente = (
        db.query(Estoque)
        .filter(
            Estoque.unidade_id == dados.unidade_id,
            Estoque.produto_id == dados.produto_id,
        )
        .first()
    )

    if estoque_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Estoque já cadastrado para este produto nesta unidade",
        )

    estoque = Estoque(
        unidade_id=dados.unidade_id,
        produto_id=dados.produto_id,
        quantidade=dados.quantidade,
    )

    db.add(estoque)
    db.commit()
    db.refresh(estoque)

    return estoque


@router.get(
    "",
    response_model=list[EstoqueResposta],
)
def listar_estoques(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return db.query(Estoque).all()


@router.patch(
    "/{estoque_id}/entrada",
    response_model=EstoqueResposta,
)
def entrada_estoque(
    estoque_id: int,
    dados: EstoqueMovimentacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    estoque = (
        db.query(Estoque)
        .filter(Estoque.id == estoque_id)
        .first()
    )

    if estoque is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estoque não encontrado",
        )

    estoque.quantidade += dados.quantidade

    db.commit()
    db.refresh(estoque)

    return estoque


@router.patch(
    "/{estoque_id}/saida",
    response_model=EstoqueResposta,
)
def saida_estoque(
    estoque_id: int,
    dados: EstoqueMovimentacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    estoque = (
        db.query(Estoque)
        .filter(Estoque.id == estoque_id)
        .first()
    )

    if estoque is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estoque não encontrado",
        )

    if estoque.quantidade < dados.quantidade:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Estoque insuficiente",
        )

    estoque.quantidade -= dados.quantidade

    db.commit()
    db.refresh(estoque)

    return estoque