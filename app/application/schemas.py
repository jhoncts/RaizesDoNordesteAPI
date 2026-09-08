from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import CanalPedido, PerfilUsuario, StatusPedido


class UsuarioCriacao(BaseModel):
    nome: str
    email: EmailStr
    senha: str


class UsuarioResposta(BaseModel):
    id: int
    nome: str
    email: EmailStr
    perfil: PerfilUsuario
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class UnidadeCriacao(BaseModel):
    nome: str
    endereco: str
    cidade: str


class UnidadeResposta(BaseModel):
    id: int
    nome: str
    endereco: str
    cidade: str
    ativa: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ProdutoCriacao(BaseModel):
    nome: str
    descricao: str | None = None
    preco: Decimal


class ProdutoResposta(BaseModel):
    id: int
    nome: str
    descricao: str | None
    preco: Decimal
    ativo: bool
    criado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class EstoqueCriacao(BaseModel):
    unidade_id: int
    produto_id: int
    quantidade: int = Field(ge=0)


class EstoqueMovimentacao(BaseModel):
    quantidade: int = Field(gt=0)


class EstoqueResposta(BaseModel):
    id: int
    unidade_id: int
    produto_id: int
    quantidade: int
    atualizado_em: datetime

    model_config = ConfigDict(from_attributes=True)


class ItemPedidoCriacao(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class PedidoCriacao(BaseModel):
    unidade_id: int
    canal_pedido: CanalPedido = Field(alias="canalPedido")
    itens: list[ItemPedidoCriacao] = Field(min_length=1)

    model_config = ConfigDict(populate_by_name=True)


class ItemPedidoResposta(BaseModel):
    id: int
    produto_id: int
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class PedidoResposta(BaseModel):
    id: int
    usuario_id: int
    unidade_id: int
    canal_pedido: CanalPedido = Field(alias="canalPedido")
    status: StatusPedido
    valor_total: Decimal
    criado_em: datetime
    atualizado_em: datetime

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )