from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.application.auth_service import obter_usuario_atual
from app.application.permissions import exigir_gerente
from app.application.schemas import UnidadeCriacao, UnidadeResposta
from app.infrastructure.database import get_db
from app.infrastructure.models import Unidade, Usuario


router = APIRouter(
    prefix="/unidades",
    tags=["Unidades"],
)


@router.post(
    "",
    response_model=UnidadeResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_unidade(
    dados: UnidadeCriacao,
    db: Session = Depends(get_db),
    gerente: Usuario = Depends(exigir_gerente),
):
    unidade = Unidade(
        nome=dados.nome,
        endereco=dados.endereco,
        cidade=dados.cidade,
    )

    db.add(unidade)
    db.commit()
    db.refresh(unidade)

    return unidade


@router.get(
    "",
    response_model=list[UnidadeResposta],
)
def listar_unidades(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(obter_usuario_atual),
):
    return db.query(Unidade).all()