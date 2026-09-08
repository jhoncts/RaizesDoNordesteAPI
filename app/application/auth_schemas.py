from pydantic import BaseModel, EmailStr


class LoginDados(BaseModel):
    email: EmailStr
    senha: str


class TokenResposta(BaseModel):
    access_token: str
    token_type: str = "bearer"