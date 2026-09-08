from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.errors import (
    ErroResposta,
    ErroValidacaoResposta,
)
from app.application.schemas import (
    ConsentimentoFidelidadeAtualizacao,
    ResgateFidelidadeEntrada,
    ResgateFidelidadeResposta,
    UsuarioCriacao,
    UsuarioResposta,
)
from app.domain.enums import PerfilUsuario
from app.infrastructure.database import get_db
from app.infrastructure.models import Auditoria, Usuario
from app.infrastructure.security import gerar_hash_senha


router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"],
)


@router.post(
    "",
    response_model=UsuarioResposta,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "model": ErroResposta,
            "description": "E-mail já cadastrado",
        },
        422: {
            "model": ErroValidacaoResposta,
            "description": "Erro de validação dos dados enviados",
        },
    },
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


@router.patch(
    "/me/consentimento-fidelidade",
    response_model=UsuarioResposta,
    responses={
        401: {
            "model": ErroResposta,
            "description": "Não autenticado ou token inválido",
        },
        422: {
            "model": ErroValidacaoResposta,
            "description": "Erro de validação dos dados enviados",
        },
    },
)
def atualizar_consentimento_fidelidade(
    dados: ConsentimentoFidelidadeAtualizacao,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    usuario.consentimento_fidelidade = dados.consentimento

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="ALTERACAO_CONSENTIMENTO_FIDELIDADE",
        entidade="Usuario",
        entidade_id=usuario.id,
        detalhes=(
            "Consentimento de fidelidade alterado para "
            f"{dados.consentimento}"
        ),
    )

    db.add(auditoria)
    db.commit()
    db.refresh(usuario)

    return usuario


@router.post(
    "/me/fidelidade/resgatar",
    response_model=ResgateFidelidadeResposta,
    responses={
        401: {
            "model": ErroResposta,
            "description": "Não autenticado ou token inválido",
        },
        409: {
            "model": ErroResposta,
            "description": (
                "Programa de fidelidade sem consentimento "
                "ou saldo de pontos insuficiente"
            ),
        },
        422: {
            "model": ErroValidacaoResposta,
            "description": "Erro de validação dos dados enviados",
        },
    },
)
def resgatar_pontos_fidelidade(
    dados: ResgateFidelidadeEntrada,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    if not usuario.consentimento_fidelidade:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="É necessário consentir com o programa de fidelidade",
        )

    if usuario.pontos_fidelidade < dados.pontos:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Saldo de pontos insuficiente",
        )

    usuario.pontos_fidelidade -= dados.pontos

    auditoria = Auditoria(
        usuario_id=usuario.id,
        acao="RESGATE_PONTOS_FIDELIDADE",
        entidade="Usuario",
        entidade_id=usuario.id,
        detalhes=f"Resgate de {dados.pontos} pontos de fidelidade",
    )

    db.add(auditoria)
    db.commit()
    db.refresh(usuario)

    return ResgateFidelidadeResposta(
        pontos_resgatados=dados.pontos,
        saldo_pontos=usuario.pontos_fidelidade,
        mensagem="Resgate de pontos realizado com sucesso",
    )