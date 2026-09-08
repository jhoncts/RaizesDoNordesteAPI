from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

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