from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth_schemas import LoginDados, TokenResposta
from app.application.auth_service import (
    autenticar_usuario,
    criar_access_token,
    obter_usuario_atual,
)
from app.application.errors import (
    ErroResposta,
    ErroValidacaoResposta,
)
from app.application.schemas import UsuarioResposta
from app.infrastructure.database import get_db
from app.infrastructure.models import Usuario


router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)


@router.post(
    "/login",
    response_model=TokenResposta,
    responses={
        401: {
            "model": ErroResposta,
            "description": "E-mail ou senha inválidos",
        },
        422: {
            "model": ErroValidacaoResposta,
            "description": "Erro de validação dos dados enviados",
        },
    },
)
def login(
    dados: LoginDados,
    db: Session = Depends(get_db),
):
    usuario = autenticar_usuario(
        dados.email,
        dados.senha,
        db,
    )

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
        )

    token = criar_access_token(usuario)

    return TokenResposta(
        access_token=token,
        token_type="bearer",
    )


@router.get(
    "/me",
    response_model=UsuarioResposta,
    responses={
        401: {
            "model": ErroResposta,
            "description": "Não autenticado ou token inválido",
        },
    },
)
def usuario_atual(
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return usuario