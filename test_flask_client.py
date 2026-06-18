# test_flask_client.py — Sprint 4 (Parte Central)
#
# Refatoração do test_ia_gerado.py para Flask test client.
# NÃO usa requests HTTP — importa o app diretamente.
# Pré-requisito arquitetural para o mutmut funcionar
# (JIA; HARMAN, 2011, p. 651 — independência de servidor externo).
#
# A fixture 'client' e o reset do banco estão no conftest.py.

import pytest


# ──────────────────────────────────────────────────────────────
# GET /saldo/<conta_id>
# ──────────────────────────────────────────────────────────────

def test_saldo_alice(client):
    """Alice (conta 1) tem saldo inicial de R$1000,00."""
    resp = client.get("/saldo/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["conta_id"] == 1
    assert data["titular"] == "Alice"
    assert data["saldo"] == 1000.00


def test_saldo_bob(client):
    """Bob (conta 2) tem saldo inicial de R$500,00."""
    resp = client.get("/saldo/2")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["conta_id"] == 2
    assert data["titular"] == "Bob"
    assert data["saldo"] == 500.00


def test_saldo_carlos(client):
    """Carlos (conta 3) tem saldo inicial de R$0,00."""
    resp = client.get("/saldo/3")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["conta_id"] == 3
    assert data["titular"] == "Carlos"
    assert data["saldo"] == 0.00


def test_saldo_conta_inexistente(client):
    """Conta 999 não existe — deve retornar 404."""
    resp = client.get("/saldo/999")
    assert resp.status_code == 404
    assert "erro" in resp.get_json()


# ──────────────────────────────────────────────────────────────
# POST /transferencia
# ──────────────────────────────────────────────────────────────

def test_transferencia_valida(client):
    """Transferência válida — deve retornar 200 e mensagem de sucesso."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 100.00
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["mensagem"] == "Transferencia realizada"
    assert data["valor"] == 100.00


def test_transferencia_saldo_igual_valor(client):
    """
    # Primeiro teste TDD — caso de borda crítico.
    Transferência com valor EXATAMENTE IGUAL ao saldo deve ser PERMITIDA.
    Mata mutante que troca '<' por '<=' na verificação de saldo insuficiente.
    """
    resp = client.post("/transferencia", json={
        "origem": 2,    # Bob tem R$500,00
        "destino": 3,
        "valor": 500.00
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["mensagem"] == "Transferencia realizada"
    assert float(data["valor"]) == 500.00

    # Verifica saldo atualizado (mata mutantes de UPDATE invertido)
    bob = client.get("/saldo/2").get_json()
    carlos = client.get("/saldo/3").get_json()
    assert bob["saldo"] == 0.00
    assert carlos["saldo"] == 500.00

    # Verifica extrato (mata mutantes de INSERT em transferencias)
    extrato_bob = client.get("/extrato/2").get_json()
    assert extrato_bob["saldo_atual"] == 0.00
    assert any(
        t["origem"] == 2 and t["destino"] == 3 and float(t["valor"]) == 500.00
        for t in extrato_bob["historico"]
    )


def test_transferencia_saldo_suficiente(client):
    """Transferência com saldo suficiente — verifica saldo após a operação."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 100.00
    })
    assert resp.status_code == 200

    alice = client.get("/saldo/1").get_json()
    bob = client.get("/saldo/2").get_json()
    assert alice["saldo"] == 900.00
    assert bob["saldo"] == 600.00


def test_transferencia_saldo_insuficiente(client):
    """Transferência com saldo insuficiente — deve retornar 422."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 9999.00
    })
    assert resp.status_code == 422
    data = resp.get_json()
    assert "Saldo insuficiente" in data["erro"]
    assert "saldo_atual" in data


def test_transferencia_valor_negativo(client):
    """Valor negativo — deve retornar 422."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": -50.00
    })
    assert resp.status_code == 422
    assert resp.get_json()["erro"] == "Valor deve ser positivo"


def test_transferencia_valor_zero(client):
    """Valor zero — deve retornar 422."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 2, "valor": 0
    })
    assert resp.status_code == 422
    assert resp.get_json()["erro"] == "Valor deve ser positivo"


def test_transferencia_origem_destino_iguais(client):
    """Origem igual ao destino — deve retornar 422."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 1, "valor": 50.00
    })
    assert resp.status_code == 422
    assert "iguais" in resp.get_json()["erro"]


def test_transferencia_conta_origem_inexistente(client):
    """Conta de origem 999 não existe — deve retornar 404."""
    resp = client.post("/transferencia", json={
        "origem": 999, "destino": 2, "valor": 100.00
    })
    assert resp.status_code == 404


def test_transferencia_conta_destino_inexistente(client):
    """Conta de destino 999 não existe — deve retornar 404."""
    resp = client.post("/transferencia", json={
        "origem": 1, "destino": 999, "valor": 100.00
    })
    assert resp.status_code == 404


def test_transferencia_campos_ausentes(client):
    """Corpo JSON sem campos obrigatórios — deve retornar 400."""
    resp = client.post("/transferencia", json={"origem": 1})
    assert resp.status_code == 400
    assert "ausentes" in resp.get_json()["erro"]


def test_transferencia_corpo_invalido(client):
    """Corpo não-JSON — deve retornar 400."""
    resp = client.post(
        "/transferencia",
        data="nao e json",
        content_type="text/plain"
    )
    assert resp.status_code == 400


# ──────────────────────────────────────────────────────────────
# GET /extrato/<conta_id>
# ──────────────────────────────────────────────────────────────

def test_extrato_conta_existente(client):
    """Extrato da conta 1 deve retornar 200 com histórico."""
    resp = client.get("/extrato/1")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["conta_id"] == 1
    assert "historico" in data
    assert isinstance(data["historico"], list)


def test_extrato_conta_inexistente(client):
    """Extrato de conta 999 não existe — deve retornar 404."""
    resp = client.get("/extrato/999")
    assert resp.status_code == 404
    assert "erro" in resp.get_json()
