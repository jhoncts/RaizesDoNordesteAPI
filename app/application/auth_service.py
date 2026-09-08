from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.infrastructure.config import settings
from app.infrastructure.database import get_db
from app.infrastructure.models import Usuario
from app.infrastructure.security import verificar_senha


bearer_scheme = HTTPBearer()


def autenticar_usuario(
    email: str,
    senha: str,
    db: Session,
) -> Usuario | None:
    usuario = (
        db.query(Usuario)
        .filter(Usuario.email == email)
        .first()
    )

    if usuario is None:
        return None

    if not usuario.ativo:
        return None

    if not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario


def criar_access_token(usuario: Usuario) -> str:
    expiracao = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(usuario.id),
        "perfil": usuario.perfil.value,
        "exp": expiracao,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def obter_usuario_atual(
    credenciais: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    try:
        payload = jwt.decode(
            credenciais.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        usuario_id = int(payload["sub"])

    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )

    usuario = (
        db.query(Usuario)
        .filter(Usuario.id == usuario_id)
        .first()
    )

    if usuario is None or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    return usuario