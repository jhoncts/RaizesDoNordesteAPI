from fastapi import FastAPI

app = FastAPI(
    title="Raízes do Nordeste API",
    version="0.1.0",
)

@app.get("/")
def inicio():
    return {"mensagem": "API Raízes do Nordeste funcionando"}