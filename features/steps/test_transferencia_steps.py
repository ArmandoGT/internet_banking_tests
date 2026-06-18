import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from app import app, init_db

# Lê os cenários definidos no arquivo .feature
scenarios("../transferencia.feature")

@pytest.fixture
def contexto():
    """Dicionário para compartilhar estado entre os steps de um mesmo cenário."""
    return {}

def caminho_banco():
    """Retorna o caminho do banco de dados configurado no app."""
    return os.path.abspath(app.config["DATABASE"])

@given("que o banco de dados foi removido")
def banco_de_dados_foi_removido():
    """Garante que o banco de dados seja removido antes de inicializar."""
    db_path = caminho_banco()
    if os.path.exists(db_path):
        os.remove(db_path)

@when("o sistema inicializa o banco de dados")
def sistema_inicializa_banco(contexto):
    """Chama a função de inicialização real do app.py."""
    init_db()
    contexto["inicializado"] = True

@then(parsers.parse("a conta {conta_id:d} deve existir com saldo {saldo_esperado:f}"))
def conta_deve_existir_com_saldo(client, conta_id, saldo_esperado):
    """Verifica se a conta foi criada corretamente com o saldo esperado usando o test client."""
    resposta = client.get(f"/saldo/{conta_id}")
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert float(dados["saldo"]) == saldo_esperado

@then(parsers.parse("a consulta da conta {conta_id:d} deve retornar status {status:d}"))
def consulta_da_conta_deve_retornar_status(client, conta_id, status):
    """Verifica se a resposta do endpoint de saldo é o status esperado."""
    resposta = client.get(f"/saldo/{conta_id}")
    assert resposta.status_code == status
