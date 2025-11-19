
  

# Backend do Gestor de Phishing

Vou te ensinar a rodar o backend

## Passo a passo

Todos os comando que você precisa usar para rodar o backend  

### Devem ser usados na primeira vez (configurar)

1. Criar virtual enviorment

```
python -m venv ./venv
```

2. Ativar o venv (no codespaces)
```
source venv/bin/activate
```

3. Baixar dependências no venv
```
pip install -r requirements.txt
```

4. Veja se o docker do banco esta rodando

> Se não tiver da seus pulos


5. Entrar na pasta do projeto
```
cd app
```

6. Criar banco de dados
```
flask create-db
```

7. Adicionar conta de admin

```
flask add-admin
```

### Devem se usados toda vez

1. Ativar o venv (no codespaces)

```
source venv/bin/activate
```

2. Entrar na pasta do projeto

```
cd app
```

3. Rodar servidor

```
flask run
```

### Comandos adicionais

- Apagar o banco de dados
> Se usar isso tem q criar o banco e adicionar o admin dnv
```
flask drop-db
```

- Rodar campanha
```
flask run-campaign <id da campanha>
```

- Encerrar campanha
```
flask end-campaign <id da campanha>
```

## Informações importantes

### Conta de admin
Informações de acesso da conta de administrador
> Recomendo so usar ele para criar outras contas
- usuario : `admin`
- senha: `teste`

### Autenticação
O sistema utiliza de JWT para autenticação stateless. 
> Rant sobre JWT: 
> JSON Web Token é um token de acesso que é passado no cabeçalho da requisição, nele é contido informações que permitem o servidor descobrir qual é o usuário que esta acessando a página.
> 
> Um JWT possui três partes:
>1. Um texto em base64 que diz que isto é um JWT. É igual para todos é so pra deixar claro mesmo
>2. Os dados do usuário em base64. Nos só guardamos o id do usurário e se ele é admin ou não. Esses dados podem ser lidos pelo usuario caso ele procure mas não podem ser editados.
>3. Uma chave de validação. Essa chave é criada pelo servidor com base nos dados do segundo campo e em uma chave secreta que esta guardada nas configurações do servidor. Caso os dados do usuário tenham sido alterados, (já que é apenas uma string em base64) a chave de validação não vai coincidir com o dados, assim impedindo o acesso do usuário.

Para que você possa adquirir o seu próprio JWT você deve acessar `/api/v1/auth` com o metodo `POST` passando os parâmetros `name` e `password`

> voce pode testar isso na pagina do swagger que fica em `api/v1/`

Assim ao adquirir seu token você terá que o colocar no cabeçalho da requisição da seguinte forma:
```
Authorization: Bearer <token>
```
### Swagger
Para saber quais são as rotas e o que elas pedem você pode acessar a pagina do swagger em `/api/v1`