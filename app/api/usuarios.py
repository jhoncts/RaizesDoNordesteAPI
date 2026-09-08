from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.schemas import UsuarioCriacao, UsuarioResposta
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models import Usuario
from app.infrastructure.security import gerar_hash_senha


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)


@router.post(
    "",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_usuario(
    dados: UsuarioCriacao,
    db: Session = Depends(get_db),
):
    usuario_existente = (
        db.query(Usuario)
        .filter(Usuario.email == dados.email)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )

    usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=gerar_hash_senha(dados.senha),
        perfil=PerfilUsuario.CLIENTE,
    )

    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario