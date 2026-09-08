from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.usuarios import router as usuarios_router


app = FastAPI(
    title="Raízes do Nordeste API",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(usuarios_router)


@app.get("/")
def inicio():
    return {"mensagem": "API Raízes do Nordeste funcionando"}