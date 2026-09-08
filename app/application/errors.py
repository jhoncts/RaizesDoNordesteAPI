from typing import Any

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErroDetalhe(BaseModel):
    status: int
    mensagem: str
    caminho: str


class ErroResposta(BaseModel):
    erro: ErroDetalhe


class ErroValidacaoDetalhe(ErroDetalhe):
    detalhes: list[dict[str, Any]]


class ErroValidacaoResposta(BaseModel):
    erro: ErroValidacaoDetalhe


async def tratar_erro_http(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": {
                "status": exc.status_code,
                "mensagem": exc.detail,
                "caminho": request.url.path,
            }
        },
        headers=exc.headers,
    )


async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "erro": {
                    "status": 422,
                    "mensagem": "Erro de validação dos dados enviados",
                    "caminho": request.url.path,
                    "detalhes": exc.errors(),
                }
            }
        ),
    )