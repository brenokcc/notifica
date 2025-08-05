# ArboNotifica

*ArboNotifica* consiste em um *sistema Web* que também pode ser utilizado como *aplicativo* para dispositivos móveis (tablets e celular).
    
O sistema tem por objetivo registrar as notificações de arboviroses a fim de tornar a tomada de decisão mais célere, uma vez que o acompanhamento das notificações poderá ser feito em tempo real.

A abordagem tradicional através do preenchimento de fichas em papel acarreta alguns problemas, os quais são resolvidos pela utilização do sistema. Dentre os principais benefícios do uso do sistema pode-se destacar:
- Facilidade do preenchimento do formulário, pois ele pode ser montado dinamicamente baseado nas respostas que são fornecidas durante o cadastro da notificação.
- Possibilidade de validação dos dados baseada em regras pré-estabelecidas
- Preenchimento automático dos dados do paciente através de consultas a sistemas de informação existentes como o e-SUS.



## Pré-Requisito

É necessária a criação do banco de dados para que a aplicação possa ser inicialidada com Docker.

```
createdb -U postgres arbonotifica
```

## Configuração

Para configurar as variáveis de ambiente da aplicação, copie o arquivo "sample.env" para ".env" e realize as defidas alterações.

```
cp sample.env .env
vim .env
```

## Inicialização

```
docker compose up -d --build --force-recreate
```

## Finalização

```
docker compose down
```

## Atualização

```
git pull origin main
docker compose exec app python manage.py sync
```