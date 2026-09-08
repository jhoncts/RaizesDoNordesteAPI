from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.permissions import (
    exigir_atendente_ou_gerente,
    exigir_cozinha_ou_gerente,
)
from app.application.schemas import (
    ItemPedidoResposta,
    PedidoCriacao,
    PedidoResposta,
)
from app.domain.enums import CanalPedido, StatusPedido
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Auditoria,
    Estoque,
    ItemPedido,
    Pedido,
    Produto,
    Unidade,
    Usuario,
)


router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"],
)


@router.post(
    "",
    response_model=PedidoResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_pedido(
    dados: PedidoCriacao,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    unidade = (
        db.query(Unidade)
        .filter(Unidade.id == dados.unidade_id)
        .first()
    )

    if unidade is None or not unidade.ativa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidade não encontrada",
        )

    quantidades_por_produto = {}

    for item in dados.itens:
        quantidades_por_produto[item.produto_id] = (
            quantidades_por_produto.get(item.produto_id, 0)
            + item.quantidade
        )

    valor_total = Decimal("0.00")
    itens_processados = []

    for produto_id, quantidade in quantidades_por_produto.items():
        produto = (
            db.query(Produto)
            .filter(Produto.id == produto_id)
            .first()
        )

        if produto is None or not produto.ativo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Produto não encontrado",
            )

        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.unidade_id == dados.unidade_id,
                Estoque.produto_id == produto_id,
            )
            .first()
        )

        if estoque is None or estoque.quantidade < quantidade:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Estoque insuficiente",
            )

        subtotal = produto.preco * quantidade
        valor_total += subtotal

        itens_processados.append(
            {
                "produto": produto,
                "estoque": estoque,
                "quantidade": quantidade,
                "subtotal": subtotal,
            }
        )

    pedido = Pedido(
        usuario_id=usuario.id,
        unidade_id=dados.unidade_id,
        canal_pedido=dados.canal_pedido,
        status=StatusPedido.AGUARDANDO_PAGAMENTO,
        valor_total=valor_total,
    )

    db.add(pedido)
    db.flush()

    for item in itens_processados:
        item_pedido = ItemPedido(
            pedido_id=pedido.id,
            produto_id=item["produto"].id,
            quantidade=item["quantidade"],
            preco_unitario=item["produto"].preco,
            subtotal=item["subtotal"],
        )

        db.add(item_pedido)

        item["estoque"].quantidade -= item["quantidade"]

    db.commit()
    db.refresh(pedido)

    return pedido


@router.get(
    "",
    response_model=list[PedidoResposta],
)
def listar_pedidos(
    canal_pedido: CanalPedido | None = Query(
        default=None,
        alias="canalPedido",
    ),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    consulta = (
        db.query(Pedido)
        .filter(Pedido.usuario_id == usuario.id)
    )

    if canal_pedido is not None:
        consulta = consulta.filter(
            Pedido.canal_pedido == canal_pedido
        )

    return consulta.order_by(Pedido.id.desc()).all()


@router.get(
    "/{pedido_id}/itens",
    response_model=list[ItemPedidoResposta],
)
def listar_itens_pedido(
    pedido_id: int,
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

    itens = (
        db.query(ItemPedido)
        .filter(ItemPedido.pedido_id == pedido_id)
        .order_by(ItemPedido.id)
        .all()
    )

    return itens


@router.patch(
    "/{pedido_id}/pronto",
    response_model=PedidoResposta,
)
def marcar_pedido_pronto(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_cozinha_ou_gerente),
):
    pedido = (
        db.query(Pedido)
        .filter(Pedido.id == pedido_id)
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )

    if pedido.status != StatusPedido.EM_PREPARO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pedido não está em preparo",
        )

    status_anterior = pedido.status
    pedido.status = StatusPedido.PRONTO

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="ALTERACAO_STATUS_PEDIDO",
        entidade="Pedido",
        entidade_id=pedido.id,
        detalhes=(
            f"Status alterado de "
            f"{status_anterior.value} para {pedido.status.value}"
        ),
    )

    db.add(auditoria)
    db.commit()
    db.refresh(pedido)

    return pedido


@router.patch(
    "/{pedido_id}/entregue",
    response_model=PedidoResposta,
)
def marcar_pedido_entregue(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(exigir_atendente_ou_gerente),
):
    pedido = (
        db.query(Pedido)
        .filter(Pedido.id == pedido_id)
        .first()
    )

    if pedido is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )

    if pedido.status != StatusPedido.PRONTO:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Pedido não está pronto",
        )

    status_anterior = pedido.status
    pedido.status = StatusPedido.ENTREGUE

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="ALTERACAO_STATUS_PEDIDO",
        entidade="Pedido",
        entidade_id=pedido.id,
        detalhes=(
            f"Status alterado de "
            f"{status_anterior.value} para {pedido.status.value}"
        ),
    )

    db.add(auditoria)
    db.commit()
    db.refresh(pedido)

    return pedido