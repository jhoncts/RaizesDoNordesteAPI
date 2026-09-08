# Raízes do Nordeste API

API REST desenvolvida para o Projeto Multidisciplinar do curso de Análise e Desenvolvimento de Sistemas.

O projeto utiliza como estudo de caso a rede fictícia **Raízes do Nordeste** e representa operações como cadastro de usuários, unidades, produtos, controle de estoque, pedidos e pagamentos.

## Funcionalidades

Entre as principais funcionalidades implementadas estão:

- cadastro e autenticação de usuários;
- autenticação por JWT;
- controle de acesso por perfil;
- gerenciamento de unidades e produtos;
- cardápio por unidade;
- controle de estoque;
- criação e consulta de pedidos;
- pedidos por diferentes canais de atendimento;
- pagamento simulado;
- atualização do status dos pedidos;
- cancelamento de pedidos;
- programa de fidelidade mediante consentimento;
- registro de operações para auditoria;
- tratamento padronizado de erros;
- documentação da API com Swagger.

Os canais disponíveis para pedidos são:

- `APP`
- `WEB`
- `TOTEM`
- `BALCAO`
- `PICKUP`

O fluxo principal implementado é:

```text
Pedido criado
→ Aguardando pagamento
→ Em preparo
→ Pronto
→ Entregue
```

Caso o pagamento seja recusado, o pedido passa para `PAGAMENTO_RECUSADO` e os itens reservados retornam ao estoque.

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
- PlantUML

As dependências utilizadas estão disponíveis no arquivo:

```text
requirements.txt
```

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
│   └── main.py
├── docs/
│   ├── diagramas/
│   └── evidencias/
├── postman/
│   └── RaizesDoNordesteAPI.postman_collection.json
├── tests/
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

A aplicação foi dividida em camadas:

- `api`: rotas HTTP da aplicação;
- `application`: schemas, autenticação, permissões e tratamento de erros;
- `domain`: enums utilizados pelo sistema;
- `infrastructure`: banco de dados, models, segurança, configuração e seed;
- `tests`: testes automatizados.

## Requisitos

Para executar o projeto é necessário ter instalado:

- Python 3.12;
- pip;
- Git.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/jhoncts/RaizesDoNordesteAPI.git
cd RaizesDoNordesteAPI
```

Crie um ambiente virtual:

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

Crie um arquivo `.env` na raiz do projeto utilizando o `.env.example` como referência.

Exemplo:

```env
DATABASE_URL=sqlite:///./raizes_nordeste.db
JWT_SECRET_KEY=troque-por-uma-chave-secreta-segura
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

A chave utilizada em `JWT_SECRET_KEY` deve ser substituída por uma chave própria.

O arquivo `.env` não deve ser publicado no repositório.

## Banco de dados

O projeto utiliza SQLite e as alterações da estrutura do banco são controladas pelo Alembic.

Execute as migrations:

```bash
alembic upgrade head
```

Depois execute o seed:

```bash
python -m app.infrastructure.seed
```

O seed cria os dados iniciais utilizados para demonstração:

- usuário gerente;
- unidade;
- produto;
- estoque inicial.

O script verifica se os registros já existem antes de criá-los.

### Usuário gerente de demonstração

```text
E-mail: gerente@empresa.com.br
Senha: 123456
Perfil: GERENTE
```

As credenciais acima são utilizadas somente para testes locais e demonstração do projeto.

## Executando a API

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

## Swagger

A documentação interativa da API pode ser acessada em:

```text
http://127.0.0.1:8000/docs
```

Também está disponível o ReDoc:

```text
http://127.0.0.1:8000/redoc
```

No Swagger é possível visualizar os endpoints, parâmetros, schemas e códigos de resposta utilizados pela API.

## Autenticação

O login é realizado pelo endpoint:

```text
POST /auth/login
```

Exemplo:

```json
{
  "email": "gerente@empresa.com.br",
  "senha": "123456"
}
```

Após o login, a API retorna um `access_token`.

Esse token deve ser utilizado nas rotas protegidas:

```text
Authorization: Bearer <token>
```

As senhas dos usuários são armazenadas utilizando hash e não ficam registradas em texto puro.

## Perfis de acesso

A aplicação possui quatro perfis:

| Perfil | Função |
| --- | --- |
| `CLIENTE` | Realização e consulta de pedidos |
| `ATENDENTE` | Operações relacionadas à entrega |
| `COZINHA` | Atualização do preparo dos pedidos |
| `GERENTE` | Operações administrativas |

As permissões são verificadas antes da execução das rotas protegidas.

## Pedidos e pagamentos

Um pedido é criado inicialmente com o status:

```text
AGUARDANDO_PAGAMENTO
```

Quando o pagamento é aprovado:

```text
AGUARDANDO_PAGAMENTO
→ EM_PREPARO
→ PRONTO
→ ENTREGUE
```

Quando o pagamento é recusado:

```text
AGUARDANDO_PAGAMENTO
→ PAGAMENTO_RECUSADO
```

O pagamento é realizado por meio de uma simulação:

```text
POST /pagamentos/mock/{pedido_id}
```

Exemplo de pagamento aprovado:

```json
{
  "aprovado": true
}
```

Exemplo de pagamento recusado:

```json
{
  "aprovado": false
}
```

Os pedidos também podem ser filtrados pelo canal utilizado:

```text
GET /pedidos?canalPedido=APP
```

## Estoque

O estoque é controlado por unidade e produto.

Antes da criação do pedido, a API verifica se existe quantidade disponível.

Quando não há estoque suficiente, a operação retorna:

```text
409 Conflict
```

Quando um pagamento é recusado ou um pedido aguardando pagamento é cancelado, os itens são devolvidos ao estoque.

## Fidelidade

O programa de fidelidade depende do consentimento do usuário.

O consentimento pode ser alterado pelo endpoint:

```text
PATCH /usuarios/me/consentimento-fidelidade
```

O resgate de pontos é realizado em:

```text
POST /usuarios/me/fidelidade/resgatar
```

A aplicação impede o resgate quando não existe consentimento ou quando o saldo de pontos é insuficiente.

## Auditoria

Algumas operações geram registros de auditoria, como:

- processamento de pagamento;
- cancelamento de pedido;
- alteração do status do pedido;
- alteração do consentimento de fidelidade;
- resgate de pontos.

Os registros armazenam informações sobre a ação realizada, usuário, entidade relacionada e data da operação.

## Tratamento de erros

A API utiliza respostas de erro padronizadas.

Exemplo:

```json
{
  "erro": {
    "status": 409,
    "mensagem": "Estoque insuficiente",
    "caminho": "/pedidos"
  }
}
```

Entre os principais códigos utilizados estão:

- `401` - não autenticado;
- `403` - acesso sem permissão;
- `404` - recurso não encontrado;
- `409` - conflito com regra de negócio;
- `422` - erro de validação.

## Testes automatizados

Os testes foram desenvolvidos utilizando Pytest.

Para executar:

```bash
pytest -v
```

Resultado atual:

```text
12 passed
0 failed
```

Os testes incluem cenários de:

- autenticação;
- autorização;
- validação;
- pedidos;
- estoque;
- pagamento;
- cancelamento;
- fluxo completo do pedido;
- auditoria.

## Testes com Postman

A coleção utilizada está disponível em:

```text
postman/RaizesDoNordesteAPI.postman_collection.json
```

Antes de executar a coleção:

```bash
alembic upgrade head
python -m app.infrastructure.seed
uvicorn app.main:app --reload
```

Depois importe a coleção no Postman.

Caso o usuário de teste ainda não exista, execute:

```text
Criar usuario
```

Em seguida:

```text
T01 - Login valido
```

O token retornado é salvo automaticamente na variável:

```text
token
```

### Fluxo de pagamento aprovado

```text
T06 - Criar pedido valido
→ T07 - Pagamento aprovado
→ T08 - Listar pedidos por canal APP
```

O ID do pedido criado no T06 é armazenado automaticamente para utilização no T07.

### Fluxo de pagamento recusado

```text
T15 - Criar pedido para pagamento recusado
→ T16 - Pagamento recusado
→ T17 - Confirmar pedido com pagamento recusado
```

O ID criado no T15 também é armazenado automaticamente.

A coleção possui ainda cenários envolvendo respostas:

```text
401
403
404
409
422
```

## Diagramas

Os diagramas desenvolvidos estão disponíveis em:

```text
docs/diagramas/
```

Foram elaborados:

- Diagrama de Casos de Uso;
- Diagrama Entidade-Relacionamento;
- Diagrama de Classes;
- Diagrama de Arquitetura em Camadas.

Os arquivos estão disponíveis em `.puml` e `.svg`.

## Evidências

As evidências de execução estão disponíveis em:

```text
docs/evidencias/
```

A pasta possui registros da execução do:

- Swagger;
- Pytest;
- fluxo de pagamento aprovado;
- fluxo de pagamento recusado;
- filtro de pedidos;
- validação de estoque insuficiente.

## Repositório

O código-fonte, migrations, testes, coleção Postman, diagramas e evidências estão disponíveis em:

https://github.com/jhoncts/RaizesDoNordesteAPI