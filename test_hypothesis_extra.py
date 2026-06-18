import os
import sqlite3

import requests
from hypothesis import assume, given, settings, strategies as st

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")
SALDOS_INICIAIS = {1: 1000.0, 2: 500.0, 3: 0.0}


def reset_database():
    """Garante estado conhecido antes de cada exemplo gerado pelo Hypothesis."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE contas (
            id      INTEGER PRIMARY KEY,
            titular TEXT    NOT NULL,
            saldo   REAL    NOT NULL CHECK(saldo >= 0)
        );

        CREATE TABLE transferencias (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            origem    INTEGER NOT NULL,
            destino   INTEGER NOT NULL,
            valor     REAL    NOT NULL,
            data_hora TEXT    NOT NULL,
            FOREIGN KEY (origem)  REFERENCES contas(id),
            FOREIGN KEY (destino) REFERENCES contas(id)
        );

        INSERT INTO contas (id, titular, saldo) VALUES (1, 'Alice',  1000.00);
        INSERT INTO contas (id, titular, saldo) VALUES (2, 'Bob',     500.00);
        INSERT INTO contas (id, titular, saldo) VALUES (3, 'Carlos',    0.00);
        """
    )
    conn.commit()
    conn.close()


def saldo(conta_id):
    resposta = requests.get(f"{BASE_URL}/saldo/{conta_id}")
    assert resposta.status_code == 200
    return float(resposta.json()["saldo"])


@given(
    origem=st.sampled_from([1, 2, 3]),
    destino=st.sampled_from([1, 2, 3]),
    excesso=st.floats(
        min_value=0.01,
        max_value=5000.0,
        allow_nan=False,
        allow_infinity=False,
    ),
)
@settings(max_examples=30)
def test_invariante_saldo_insuficiente_sempre_rejeita_sem_alterar_saldo(origem, destino, excesso):
    reset_database()
    assume(origem != destino)

    saldo_antes = saldo(origem)
    valor = float(saldo_antes + abs(excesso))

    resposta = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": valor},
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "Saldo insuficiente"
    assert saldo(origem) == saldo_antes


@given(
    origem=st.sampled_from([1, 2]),
    destino=st.sampled_from([1, 2, 3]),
    valor=st.floats(
        min_value=0.01,
        max_value=1000.0,
        allow_nan=False,
        allow_infinity=False,
    ),
)
@settings(max_examples=30)
def test_invariante_transferencia_aceita_aparece_no_extrato(origem, destino, valor):
    reset_database()
    assume(origem != destino)
    assume(float(valor) <= SALDOS_INICIAIS[origem])

    resposta = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)},
    )
    assert resposta.status_code == 200

    extrato_origem = requests.get(f"{BASE_URL}/extrato/{origem}")
    extrato_destino = requests.get(f"{BASE_URL}/extrato/{destino}")

    assert extrato_origem.status_code == 200
    assert extrato_destino.status_code == 200

    historico_origem = extrato_origem.json()["historico"]
    historico_destino = extrato_destino.json()["historico"]

    def contem_transferencia(historico):
        return any(
            item["origem"] == origem
            and item["destino"] == destino
            and abs(float(item["valor"]) - float(valor)) < 0.000001
            and "data_hora" in item
            for item in historico
        )

    assert contem_transferencia(historico_origem)
    assert contem_transferencia(historico_destino)
