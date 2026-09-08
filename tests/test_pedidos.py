from decimal import Decimal

from app.domain.enums import PerfilUsuario, StatusPedido
from app.infrastructure.database import get_db
from app.infrastructure.models import (
    Estoque,
    Pedido,
    Produto,
    Unidade,
    Usuario,
)
from app.infrastructure.security import gerar_hash_senha


def preparar_catalogo(client, quantidade_estoque):
    override_get_db = client.app.dependency_overrides.get(get_db)

    assert override_get_db is not None

    gerador_db = override_get_db()
    db = next(gerador_db)

    try:
        unidade = Unidade(
            nome="Unidade Teste",
            endereco="Rua Teste, 100",
            cidade="Campinas",
        )

        db.add(unidade)
        db.flush()

        produto = Produto(
            nome="Baião de Dois",
            descricao="Produto de teste",
            preco=Decimal("29.90"),
        )

        db.add(produto)
        db.flush()

        estoque = Estoque(
            unidade_id=unidade.id,
            produto_id=produto.id,
            quantidade=quantidade_estoque,
        )

        db.add(estoque)
        db.commit()

        unidade_id = unidade.id
        produto_id = produto.id

        return unidade_id, produto_id

    finally:
        gerador_db.close()


def criar_cliente_e_obter_token(client, nome, email):
    resposta_usuario = client.post(
        "/usuarios",
        json={
            "nome": nome,
            "email": email,
            "senha": "123456",
        },
    )

    assert resposta_usuario.status_code == 201

    resposta_login = client.post(
        "/auth/login",
        json={
            "email": email,
            "senha": "123456",
        },
    )

    assert resposta_login.status_code == 200

    token = resposta_login.json()["access_token"]

    assert token

    return token


def test_criar_pedido_valido(client):
    token = criar_cliente_e_obter_token(
        client,
        "Cliente Pedido",
        "pedido@empresa.com.br",
    )

    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=10,
    )

    resposta = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "unidade_id": unidade_id,
            "canalPedido": "APP",
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta.status_code == 201

    dados = resposta.json()

    assert dados["status"] == "AGUARDANDO_PAGAMENTO"
    assert dados["canalPedido"] == "APP"
    assert Decimal(dados["valor_total"]) == Decimal("29.90")


def test_pedido_sem_canal_retorna_422(client):
    token = criar_cliente_e_obter_token(
        client,
        "Cliente Sem Canal",
        "semcanal@empresa.com.br",
    )

    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=10,
    )

    resposta = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "unidade_id": unidade_id,
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta.status_code == 422


def test_pedido_com_estoque_insuficiente_retorna_409(client):
    token = criar_cliente_e_obter_token(
        client,
        "Cliente Estoque",
        "estoque@empresa.com.br",
    )

    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=2,
    )

    resposta = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "unidade_id": unidade_id,
            "canalPedido": "APP",
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 10,
                }
            ],
        },
    )

    assert resposta.status_code == 409
    assert resposta.json()["erro"]["mensagem"] == "Estoque insuficiente"


def test_pagamento_aprovado(client):
    token = criar_cliente_e_obter_token(
        client,
        "Cliente Pagamento",
        "pagamento@empresa.com.br",
    )

    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=10,
    )

    resposta_pedido = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "unidade_id": unidade_id,
            "canalPedido": "APP",
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta_pedido.status_code == 201

    pedido_id = resposta_pedido.json()["id"]

    resposta_pagamento = client.post(
        f"/pagamentos/mock/{pedido_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "aprovado": True,
        },
    )

    assert resposta_pagamento.status_code == 201

    dados_pagamento = resposta_pagamento.json()

    assert dados_pagamento["status"] == "APROVADO"
    assert dados_pagamento["pedido_id"] == pedido_id
    assert Decimal(dados_pagamento["valor"]) == Decimal("29.90")

    override_get_db = client.app.dependency_overrides.get(get_db)

    assert override_get_db is not None

    gerador_db = override_get_db()
    db = next(gerador_db)

    try:
        pedido = (
            db.query(Pedido)
            .filter(Pedido.id == pedido_id)
            .first()
        )

        assert pedido is not None
        assert pedido.status == StatusPedido.EM_PREPARO

    finally:
        gerador_db.close()


def test_cancelamento_devolve_estoque(client):
    token = criar_cliente_e_obter_token(
        client,
        "Cliente Cancelamento",
        "cancelamento@empresa.com.br",
    )

    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=10,
    )

    resposta_pedido = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "unidade_id": unidade_id,
            "canalPedido": "APP",
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta_pedido.status_code == 201

    pedido_id = resposta_pedido.json()["id"]

    override_get_db = client.app.dependency_overrides.get(get_db)

    assert override_get_db is not None

    gerador_db = override_get_db()
    db = next(gerador_db)

    try:
        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.unidade_id == unidade_id,
                Estoque.produto_id == produto_id,
            )
            .first()
        )

        assert estoque is not None
        assert estoque.quantidade == 9

    finally:
        gerador_db.close()

    resposta_cancelamento = client.patch(
        f"/pedidos/{pedido_id}/cancelar",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert resposta_cancelamento.status_code == 200
    assert resposta_cancelamento.json()["status"] == "CANCELADO"

    gerador_db = override_get_db()
    db = next(gerador_db)

    try:
        estoque = (
            db.query(Estoque)
            .filter(
                Estoque.unidade_id == unidade_id,
                Estoque.produto_id == produto_id,
            )
            .first()
        )

        assert estoque is not None
        assert estoque.quantidade == 10

    finally:
        gerador_db.close()


def test_fluxo_completo_pedido(client):
    # 1. Criar cliente e obter token
    token_cliente = criar_cliente_e_obter_token(
        client,
        "Cliente Fluxo",
        "fluxo@empresa.com.br",
    )

    # 2. Preparar catálogo
    unidade_id, produto_id = preparar_catalogo(
        client,
        quantidade_estoque=10,
    )

    # 3. Criar pedido
    resposta_pedido = client.post(
        "/pedidos",
        headers={
            "Authorization": f"Bearer {token_cliente}",
        },
        json={
            "unidade_id": unidade_id,
            "canalPedido": "APP",
            "itens": [
                {
                    "produto_id": produto_id,
                    "quantidade": 1,
                }
            ],
        },
    )

    assert resposta_pedido.status_code == 201

    pedido_id = resposta_pedido.json()["id"]

    # 4. Aprovar pagamento
    resposta_pagamento = client.post(
        f"/pagamentos/mock/{pedido_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}",
        },
        json={
            "aprovado": True,
        },
    )

    assert resposta_pagamento.status_code == 201
    assert resposta_pagamento.json()["status"] == "APROVADO"

    # 5. Confirmar EM_PREPARO
    override_get_db = client.app.dependency_overrides.get(get_db)

    assert override_get_db is not None

    gerador_db = override_get_db()
    db = next(gerador_db)

    try:
        pedido = (
            db.query(Pedido)
            .filter(Pedido.id == pedido_id)
            .first()
        )

        assert pedido is not None
        assert pedido.status == StatusPedido.EM_PREPARO

        # 6. Criar gerente diretamente no banco
        gerente = Usuario(
            nome="Gerente Fluxo",
            email="gerente.fluxo@empresa.com.br",
            senha_hash=gerar_hash_senha("123456"),
            perfil=PerfilUsuario.GERENTE,
        )

        db.add(gerente)
        db.commit()

    finally:
        gerador_db.close()

    # 7. Login do gerente
    resposta_login_gerente = client.post(
        "/auth/login",
        json={
            "email": "gerente.fluxo@empresa.com.br",
            "senha": "123456",
        },
    )

    assert resposta_login_gerente.status_code == 200

    token_gerente = resposta_login_gerente.json()["access_token"]

    assert token_gerente

    # 8. Marcar pedido como PRONTO
    resposta_pronto = client.patch(
        f"/pedidos/{pedido_id}/pronto",
        headers={
            "Authorization": f"Bearer {token_gerente}",
        },
    )

    assert resposta_pronto.status_code == 200
    assert resposta_pronto.json()["status"] == "PRONTO"

    # 9. Marcar pedido como ENTREGUE
    resposta_entregue = client.patch(
        f"/pedidos/{pedido_id}/entregue",
        headers={
            "Authorization": f"Bearer {token_gerente}",
        },
    )

    assert resposta_entregue.status_code == 200
    assert resposta_entregue.json()["status"] == "ENTREGUE"