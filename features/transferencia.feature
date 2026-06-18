# language: pt
Funcionalidade: Inicialização segura do internet banking
  Como cliente do internet banking
  Quero que o sistema inicie com as contas básicas cadastradas
  Para que eu consiga consultar saldo e realizar operações bancárias com segurança

  Contexto:
    Dado que o banco de dados foi removido

  Cenário: Sistema deve criar as contas iniciais ao iniciar
    Quando o sistema inicializa o banco de dados
    Então a conta 1 deve existir com saldo 1000.00
    E a conta 2 deve existir com saldo 500.00
    E a conta 3 deve existir com saldo 0.00

  Cenário: Cliente deve conseguir consultar saldo depois da inicialização
    Quando o sistema inicializa o banco de dados
    Então a consulta da conta 1 deve retornar status 200
    E a consulta da conta 2 deve retornar status 200
    E a consulta da conta 3 deve retornar status 200
