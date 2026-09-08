from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.enums import PerfilUsuario


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