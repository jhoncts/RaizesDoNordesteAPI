def test_login_valido(client):
    cadastro = client.post(
        "/usuarios",
        json={
            "nome": "Cliente Teste",
            "email": "cliente.teste@empresa.com.br",
            "senha": "123456",
        },
    )

    assert cadastro.status_code == 201

    resposta = client.post(
        "/auth/login",
        json={
            "email": "cliente.teste@empresa.com.br",
            "senha": "123456",
        },
    )

    assert resposta.status_code == 200

    dados = resposta.json()

    assert "access_token" in dados
    assert dados["access_token"]
    assert dados["token_type"] == "bearer"


def test_login_invalido(client):
    resposta = client.post(
        "/auth/login",
        json={
            "email": "naoexiste@empresa.com.br",
            "senha": "senhaerrada",
        },
    )

    assert resposta.status_code == 401

    dados = resposta.json()

    assert dados["erro"]["status"] == 401
    assert dados["erro"]["mensagem"] == "E-mail ou senha inválidos"
    assert dados["erro"]["caminho"] == "/auth/login"


def test_rota_protegida_sem_token(client):
    resposta = client.get("/auth/me")

    assert resposta.status_code == 401

    dados = resposta.json()

    assert dados["erro"]["status"] == 401
    assert dados["erro"]["caminho"] == "/auth/me"