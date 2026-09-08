def test_api_esta_funcionando(client):
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json() == {
        "mensagem": "API Raízes do Nordeste funcionando"
    }