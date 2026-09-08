# Raízes do Nordeste API

API REST desenvolvida para o Projeto Multidisciplinar do curso de Análise e Desenvolvimento de Sistemas.

O projeto usa como estudo de caso a rede fictícia **Raízes do Nordeste** e representa algumas das principais operações de uma rede de restaurantes.

## Sobre o projeto

A API permite trabalhar com usuários, unidades, produtos, estoque, pedidos e pagamentos.

O principal fluxo implementado é o de pedidos:

```text
Pedido criado
→ Aguardando pagamento
→ Em preparo
→ Pronto
→ Entregue
```

O pagamento é simulado por um mock e pode ser aprovado ou recusado. Quando o pagamento é recusado, os produtos separados para o pedido voltam para o estoque.

Os pedidos podem ser realizados pelos seguintes canais:

- `APP`
- `WEB`
- `TOTEM`
- `BALCAO`
- `PICKUP`

O projeto também possui autenticação, controle de acesso por perfil, programa de fidelidade mediante consentimento, auditoria de algumas operações e tratamento padronizado de erros.

## Tecnologias utilizadas

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- Alembic
- Pydantic
- PyJWT
- Argon2
- Uvicorn
- Pytest
- Postman
- Git e GitHub

## Estrutura do projeto

```text
RaizesDoNordesteAPI/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   │   └── seed.py
│   └── main.py
├── postman/
│   └── RaizesDoNordesteAPI.postman_collection.json
├── tests/
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

A aplicação foi dividida em camadas para facilitar a organização do código:

- `api`: rotas da aplicação;
- `application`: schemas, autenticação, permissões e tratamento de erros;
- `domain`: enums e elementos relacionados ao domínio;
- `infrastructure`: banco de dados, models, configurações, segurança e seed;
- `tests`: testes automatizados.

## Requisitos

Para executar o projeto é necessário ter instalado:

- Python 3.12;
- pip;
- Git.

## Como executar

Clone o repositório:

```bash
git clone https://github.com/jhoncts/RaizesDoNordesteAPI.git
cd RaizesDoNordesteAPI
```

Crie o ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```bash
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração do ambiente

Crie um arquivo `.env` na raiz do projeto usando o `.env.example` como referência.

Exemplo:

```env
DATABASE_URL=sqlite:///./raizes_nordeste.db
JWT_SECRET_KEY=troque-por-uma-chave-secreta-segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

A `JWT_SECRET_KEY` deve ser substituída por uma chave própria e não deve ser publicada no repositório.

## Banco de dados

O projeto utiliza SQLite e as alterações da estrutura do banco são controladas pelo Alembic.

Para criar ou atualizar o banco:

```bash
alembic upgrade head
```

Depois de executar as migrations, rode o seed para criar os dados iniciais:

```bash
python -m app.infrastructure.seed
```

O seed cria, caso ainda não existam:

- um usuário gerente;
- uma unidade;
- um produto;
- um estoque inicial.

O script pode ser executado novamente sem criar registros duplicados.

## Iniciando a API

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

## Swagger

A documentação da API é gerada automaticamente pelo FastAPI.

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

No Swagger é possível consultar os endpoints, parâmetros, schemas e códigos de resposta da API.

## Autenticação

A autenticação é feita utilizando JWT.

O login é realizado pelo endpoint:

```text
POST /auth/login
```

Após o login, a API retorna um `access_token`.

O token deve ser enviado nas rotas protegidas no formato:

```text
Authorization: Bearer <token>
```

As senhas dos usuários são armazenadas utilizando hash e não ficam salvas em texto puro.

## Perfis de acesso

A aplicação possui quatro perfis:

| Perfil | Uso principal |
| --- | --- |
| `CLIENTE` | Realização e consulta de pedidos |
| `ATENDENTE` | Operações relacionadas à entrega |
| `COZINHA` | Atualização do preparo dos pedidos |
| `GERENTE` | Operações administrativas |

As permissões são verificadas antes da execução das rotas protegidas.

## Testes automatizados

Os testes foram desenvolvidos utilizando Pytest.

Para executar:

```bash
pytest -v
```

Resultado atual da suíte:

```text
11 passed
0 failed
```

Os testes incluem cenários positivos e negativos de autenticação, autorização, validação, estoque, pedidos, pagamentos, cancelamento e fluxo completo do pedido.

## Testes pelo Postman

A coleção utilizada nos testes está disponível em:

```text
postman/RaizesDoNordesteAPI.postman_collection.json
```

Antes dos testes, deixe a API em execução e tenha aplicado as migrations e o seed.

Para utilizar a coleção:

1. Importe o arquivo `.json` no Postman.
2. Execute `Criar usuario`, caso o usuário de teste ainda não exista.
3. Execute `T01 - Login valido`.
4. O token retornado será salvo automaticamente na variável `token`.
5. Execute os demais testes seguindo a numeração das requisições.

### Pagamento aprovado

```text
T06 - Criar pedido valido
→ T07 - Pagamento aprovado
→ T08 - Listar pedidos por canal APP
```

O T06 salva automaticamente o ID do pedido na variável `pedido_aprovado_id`, utilizada pelo T07.

### Pagamento recusado

```text
T15 - Criar pedido para pagamento recusado
→ T16 - Pagamento recusado
→ T17 - Confirmar pedido com pagamento recusado
```

O T15 salva o ID na variável `pedido_recusado_id`, utilizada pelo teste de pagamento recusado.

A coleção também possui cenários de erro envolvendo respostas `401`, `403`, `404`, `409` e `422`.

## Repositório

Código-fonte, migrations, testes e coleção Postman:

https://github.com/jhoncts/RaizesDoNordesteAPI