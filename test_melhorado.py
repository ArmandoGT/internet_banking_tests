# test_melhorado.py — Sprint 4 (Parte Central)
#
# Testes escritos especificamente para matar os mutantes SOBREVIVENTES
# identificados pelo mutmut na suíte test_flask_client.py.
#
# Abordagem: cadeia Reachability-Infection-Propagation
# (PAPADAKIS et al., 2019, p. 285).
#
# Mutantes EQUIVALENTES (não exigem teste — não mudam comportamento visível):
#   - #107 (timeout): if __name__ == "XX__main__XX" → não afeta imports
#   - #108-115: mutações em print() e app.run() dentro do bloco __main__
#               → nunca executados durante os testes (bloco inacessível)
#
# Mutantes de INSUFICIÊNCIA DA SUÍTE (exigem novos testes):
#   Ver análise abaixo por grupo.

import pytest


# ──────────────────────────────────────────────────────────────
# GRUPO 1: Mensagens de erro nos campos de resposta JSON
# Mutantes: #1, #2, #6, #7 (strings alteradas para "XX...XX")
# Estratégia: verificar o texto EXATO das mensagens de erro
# ──────────────────────────────────────────────────────────────

def test_mensagem_saldo_insuficiente_exata(client):
    """
    Mata mutante que troca "Saldo insuficiente" por "XXSaldo insuficienteXX".
    Verifica o texto exato da mensagem de erro — não apenas o status 422.
    """
    resp = client.post("/transferencia", json={
        "origem": 3,    # Carlos: saldo R$0,00
        "destino": 1,
        "valor": 1.00
    })
    assert resp.status_code == 422
    data = resp.get_json()
    assert data["erro"] == "Saldo insuficiente"


def test_campo_saldo_atual_presente_em_saldo_insuficiente(client):
    """
    Mata mutante que remove o campo "saldo_atual" da resposta 422.
    Verifica que o campo existe E tem o valor correto.
    """
    resp = client.post("/transferencia", json={
        "origem": 3,    # Carlos: saldo R$0,00
        "destino": 1,
        "valor": 50.00
    })
    assert resp.status_code == 422
    data = resp.get_json()
    assert "saldo_atual" in data
    assert data["saldo_atual"] == 0.00


# ──────────────────────────────────────────────────────────────
# GRUPO 2: Endpoint /extrato — estrutura do JSON de resposta
# Mutantes: #82–86 (chaves "titular", "saldo_atual", "historico" mutadas)
# ──────────────────────────────────────────────────────────────

def test_extrato_campos_obrigatorios_alice(client):
    """
    Mata mutantes que renomeiam chaves do JSON de extrato.
    Verifica presença E nome exato de todos os campos obrigatórios.
    """
    resp = client.get("/extrato/1")
    assert resp.status_code == 200
    data = resp.get_json()

    # Todos estes campos devem existir com o nome EXATO
    assert "conta_id" in data,    "campo 'conta_id' ausente"
    assert "titular" in data,     "campo 'titular' ausente"
    assert "saldo_atual" in data, "campo 'saldo_atual' ausente"
    assert "historico" in data,   "campo 'historico' ausente"

    # Valores iniciais conhecidos (estado resetado pelo conftest)
    assert data["conta_id"] == 1
    assert data["titular"] == "Alice"
    assert data["saldo_atual"] == 1000.00
    assert isinstance(data["historico"], list)


def test_extrato_conta_inexistente_mensagem_exata(client):
    """
    Mata mutante que troca "Conta nao encontrada" por "XXConta nao encontradaXX"
    no endpoint /extrato.
    """
    resp = client.get("/extrato/999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["erro"] == "Conta nao encontrada"


def test_extrato_reflete_transferencia_realizada(client):
    """
    Mata mutantes de INSERT em transferencias:
    Após uma transferência, o extrato deve registrar o movimento.
    Verifica que a transferência aparece no histórico de AMBAS as contas.
    """
    # Executa transferência
    client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 250.00
    })

    # Verifica extrato da conta de origem (Alice)
    extrato_alice = client.get("/extrato/1").get_json()
    assert extrato_alice["saldo_atual"] == 750.00
    assert any(
        t["origem"] == 1 and t["destino"] == 2 and float(t["valor"]) == 250.00
        for t in extrato_alice["historico"]
    ), "Transferência não aparece no extrato de Alice"

    # Verifica extrato da conta de destino (Bob)
    extrato_bob = client.get("/extrato/2").get_json()
    assert extrato_bob["saldo_atual"] == 750.00
    assert any(
        t["origem"] == 1 and t["destino"] == 2 and float(t["valor"]) == 250.00
        for t in extrato_bob["historico"]
    ), "Transferência não aparece no extrato de Bob"


# ──────────────────────────────────────────────────────────────
# GRUPO 3: Endpoint /saldo — mensagem de conta não encontrada
# Mutantes: #23, #29, #30 (texto da mensagem de erro)
# ──────────────────────────────────────────────────────────────

def test_saldo_conta_inexistente_mensagem_exata(client):
    """
    Mata mutante que altera o texto "Conta nao encontrada" no /saldo.
    Verifica o texto EXATO, não apenas o status 404.
    """
    resp = client.get("/saldo/999")
    assert resp.status_code == 404
    data = resp.get_json()
    assert data["erro"] == "Conta nao encontrada"


def test_saldo_retorna_campos_obrigatorios(client):
    """
    Mata mutantes que renomeiam chaves do JSON de /saldo.
    Verifica nome exato de todos os campos obrigatórios.
    """
    resp = client.get("/saldo/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "conta_id" in data
    assert "titular" in data
    assert "saldo" in data
    assert data["titular"] == "Alice"
    assert data["saldo"] == 1000.00


# ──────────────────────────────────────────────────────────────
# GRUPO 4: Endpoint /transferencia — mensagens de validação
# Mutantes: #15, #41, #43, #47, #54, #64, #65, #70, #94, #101
# ──────────────────────────────────────────────────────────────

def test_mensagem_valor_positivo_exata(client):
    """
    Mata mutantes que alteram o texto "Valor deve ser positivo".
    """
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 0
    })
    assert resp.status_code == 422
    assert resp.get_json()["erro"] == "Valor deve ser positivo"


def test_mensagem_origem_destino_iguais_exata(client):
    """
    Mata mutantes que alteram o texto "Origem e destino nao podem ser iguais".
    """
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 1, "valor": 100.00
    })
    assert resp.status_code == 422
    assert resp.get_json()["erro"] == "Origem e destino nao podem ser iguais"


def test_mensagem_campos_ausentes_exata(client):
    """
    Mata mutantes que alteram o texto de erro de campos ausentes.
    """
    resp = client.post("/transferencia", json={"origem": 1})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "ausentes" in data["erro"]


def test_mensagem_corpo_invalido_exata(client):
    """
    Mata mutantes que alteram o texto de erro de corpo inválido.
    """
    resp = client.post(
        "/transferencia",
        data="nao e json",
        content_type="text/plain"
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "invalido" in data["erro"] or "ausente" in data["erro"]


def test_transferencia_retorna_campos_obrigatorios(client):
    """
    Mata mutantes que alteram chaves do JSON de retorno 200.
    Verifica nome exato de "mensagem" e "valor".
    """
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 100.00
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "mensagem" in data
    assert "valor" in data
    assert data["mensagem"] == "Transferencia realizada"
    assert float(data["valor"]) == 100.00


def test_conta_inexistente_transferencia_mensagem_exata(client):
    """
    Mata mutante que altera "Conta nao encontrada" no /transferencia.
    """
    resp = client.post("/transferencia", json={
        "origem": 999, "destino": 2, "valor": 100.00
    })
    assert resp.status_code == 404
    assert resp.get_json()["erro"] == "Conta nao encontrada"
