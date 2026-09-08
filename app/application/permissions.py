from fastapi import Depends, HTTPException, status

from app.application.auth_service import obter_usuario_atual
from app.domain.enums import PerfilUsuario
from app.infrastructure.models import Usuario


def exigir_gerente(
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    if usuario.perfil != PerfilUsuario.GERENTE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para gerente",
        )

    return usuario


def exigir_cozinha_ou_gerente(
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    perfis_permitidos = {
        PerfilUsuario.COZINHA,
        PerfilUsuario.GERENTE,
    }

    if usuario.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para cozinha ou gerente",
        )

    return usuario


def exigir_atendente_ou_gerente(
    usuario: Usuario = Depends(obter_usuario_atual),
) -> Usuario:
    perfis_permitidos = {
        PerfilUsuario.ATENDENTE,
        PerfilUsuario.GERENTE,
    }

    if usuario.perfil not in perfis_permitidos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso permitido apenas para atendente ou gerente",
        )

    return usuario