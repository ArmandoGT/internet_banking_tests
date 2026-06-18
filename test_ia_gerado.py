# test_ia_gerado.py

import os
import sqlite3
import requests

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = "banking.db"


def reset_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE contas (
            id INTEGER PRIMARY KEY,
            titular TEXT NOT NULL,
            saldo REAL NOT NULL CHECK(saldo >= 0)
        );

        CREATE TABLE transferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem INTEGER NOT NULL,
            destino INTEGER NOT NULL,
            valor REAL NOT NULL,
            data_hora TEXT NOT NULL,
            FOREIGN KEY (origem) REFERENCES contas(id),
            FOREIGN KEY (destino) REFERENCES contas(id)
        );

        INSERT INTO contas (id, titular, saldo) VALUES (1, 'Alice', 1000.00);
        INSERT INTO contas (id, titular, saldo) VALUES (2, 'Bob', 500.00);
        INSERT INTO contas (id, titular, saldo) VALUES (3, 'Carlos', 0.00);
    """)
    conn.commit()
    conn.close()


def setup_function(function):
    reset_database()


def test_saldo_conta_existente():
    resp = requests.get(f"{BASE_URL}/saldo/1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["conta_id"] == 1
    assert data["titular"] == "Alice"
    assert "saldo" in data


def test_saldo_conta_inexistente():
    resp = requests.get(f"{BASE_URL}/saldo/999")
    assert resp.status_code == 404


# Primeiro teste TDD
def test_transferencia_saldo_igual_valor():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 2, "destino": 3, "valor": 500.0}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("mensagem") == "Transferencia realizada"
    assert float(data.get("valor")) == 500.0

    origem = requests.get(f"{BASE_URL}/saldo/2")
    assert origem.status_code == 200
    assert float(origem.json().get("saldo")) == 0.0

    destino = requests.get(f"{BASE_URL}/saldo/3")
    assert destino.status_code == 200
    assert float(destino.json().get("saldo")) == 500.0

    extrato_origem = requests.get(f"{BASE_URL}/extrato/2")
    assert extrato_origem.status_code == 200
    origem_data = extrato_origem.json()
    assert origem_data.get("conta_id") == 2
    assert origem_data.get("saldo_atual") == 0.0
    assert any(
        t.get("origem") == 2 and t.get("destino") == 3 and float(t.get("valor")) == 500.0 and "data_hora" in t
        for t in origem_data.get("historico", [])
    )

    extrato_destino = requests.get(f"{BASE_URL}/extrato/3")
    assert extrato_destino.status_code == 200
    destino_data = extrato_destino.json()
    assert destino_data.get("conta_id") == 3
    assert destino_data.get("saldo_atual") == 500.0
    assert any(
        t.get("origem") == 2 and t.get("destino") == 3 and float(t.get("valor")) == 500.0 and "data_hora" in t
        for t in destino_data.get("historico", [])
    )


def test_transferencia_saldo_suficiente():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 100.0}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("mensagem") == "Transferencia realizada"
    assert float(data.get("valor")) == 100.0

    origem = requests.get(f"{BASE_URL}/saldo/1")
    assert origem.status_code == 200
    assert float(origem.json().get("saldo")) == 900.0

    destino = requests.get(f"{BASE_URL}/saldo/2")
    assert destino.status_code == 200
    assert float(destino.json().get("saldo")) == 600.0


def test_transferencia_saldo_insuficiente():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 9999.0}
    )
    assert resp.status_code == 422


def test_transferencia_valor_negativo():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": -50.0}
    )
    assert resp.status_code == 422


def test_transferencia_valor_zero():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": 0}
    )
    assert resp.status_code == 422


def test_transferencia_origem_destino_iguais():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 1, "valor": 50.0}
    )
    assert resp.status_code == 422


def test_transferencia_conta_origem_inexistente():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 999, "destino": 2, "valor": 100.0}
    )
    assert resp.status_code == 404


def test_transferencia_conta_destino_inexistente():
    resp = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 999, "valor": 100.0}
    )
    assert resp.status_code == 404


def test_extrato_conta_origem_inexistente():
    resp = requests.get(f"{BASE_URL}/extrato/999")
    assert resp.status_code == 404


def test_extrato_conta_inexistente():
    resp = requests.get(f"{BASE_URL}/extrato/999")
    assert resp.status_code == 404
