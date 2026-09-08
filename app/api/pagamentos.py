from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.schemas import (
    PagamentoMockEntrada,
    PagamentoResposta,
)
from app.domain.enums import StatusPagamento, StatusPedido
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Estoque,
    ItemPedido,
    Pagamento,
    Pedido,
    Usuario,
)


router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)


@router.post(
    "/mock/{pedido_id}",
    response_model=PagamentoResposta,
    status_code=status.HTTP_201_CREATED,
)
def processar_pagamento_mock(
    pedido_id: int,
    dados: PagamentoMockEntrada,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    pedido = (
        db.query(Pedido)
        .filter(
            Pedido.id == pedido_id,
            Pedido.usuario_id == usuario.id,
        )
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )

    if pedido.status != StatusPedido.AGUARDANDO_PAGAMENTO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pedido não está aguardando pagamento",
        )

    if dados.aprovado:
        status_pagamento = StatusPagamento.APROVADO
        pedido.status = StatusPedido.EM_PREPARO

    else:
        status_pagamento = StatusPagamento.RECUSADO
        pedido.status = StatusPedido.PAGAMENTO_RECUSADO

        itens = (
            db.query(ItemPedido)
            .filter(ItemPedido.pedido_id == pedido.id)
            .all()
        )

        for item in itens:
            estoque = (
                db.query(Estoque)
                .filter(
                    Estoque.unidade_id == pedido.unidade_id,
                    Estoque.produto_id == item.produto_id,
                )
                .first()
            )

            if estoque is not None:
                estoque.quantidade += item.quantidade

    pagamento = Pagamento(
        pedido_id=pedido.id,
        status=status_pagamento,
        valor=pedido.valor_total,
        transacao_externa=f"MOCK-{uuid4().hex[:12].upper()}",
    )

    db.add(pagamento)
    db.commit()
    db.refresh(pagamento)

    return pagamento