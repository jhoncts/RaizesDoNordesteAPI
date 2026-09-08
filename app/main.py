from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.auth import router as auth_router
from app.api.estoques import router as estoques_router
from app.api.pagamentos import router as pagamentos_router
from app.api.pedidos import router as pedidos_router
from app.api.produtos import router as produtos_router
from app.api.unidades import router as unidades_router
from app.api.usuarios import router as usuarios_router
from app.application.errors import (
    tratar_erro_http,
    tratar_erro_validacao,
)


app = FastAPI(
    title="Raízes do Nordeste API",
    version="0.1.0",
)

app.add_exception_handler(
    HTTPException,
    tratar_erro_http,
)

app.add_exception_handler(
    RequestValidationError,
    tratar_erro_validacao,
)

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(unidades_router)
app.include_router(produtos_router)
app.include_router(estoques_router)
app.include_router(pedidos_router)
app.include_router(pagamentos_router)


@app.get("/")
def inicio():
    return {
        "mensagem": "API Raízes do Nordeste funcionando"
    }