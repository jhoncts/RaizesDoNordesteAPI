
def test_cliente_nao_pode_criar_unidade(client):
    resposta_usuario = client.post(
        "/usuarios",
        json={
            "nome": "Cliente Permissao",
            "email": "permissao@empresa.com.br",
            "senha": "123456",
        },
    )

    assert resposta_usuario.status_code == 201

    resposta_login = client.post(
        "/auth/login",
        json={
            "email": "permissao@empresa.com.br",
            "senha": "123456",
        },
    )

    assert resposta_login.status_code == 200

    token = resposta_login.json()["access_token"]

    resposta = client.post(
        "/unidades",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "nome": "Unidade Teste",
            "endereco": "Rua Teste, 100",
            "cidade": "Campinas",
        },
    )

    assert resposta.status_code == 403
    assert resposta.json()["erro"]["status"] == 403