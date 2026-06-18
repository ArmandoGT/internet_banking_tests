import os
import sqlite3

import requests
from hypothesis import assume, given, settings, strategies as st

BASE_URL = "http://127.0.0.1:5000"
DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")
SALDOS_INICIAIS = {1: 1000.0, 2: 500.0, 3: 0.0}
CONTAS_VALIDAS = {1, 2, 3}


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
    valor=st.floats(
        min_value=-1_000_000,
        max_value=0,
        allow_nan=False,
        allow_infinity=False,
    )
)
def test_invariante_valor_nao_positivo_sempre_rejeitado(valor):
    reset_database()

    resposta = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": 1, "destino": 2, "valor": float(valor)},
    )

    assert resposta.status_code == 422
    assert resposta.json()["erro"] == "Valor deve ser positivo"


@given(conta_id=st.integers(min_value=-9999, max_value=9999))
def test_invariante_conta_inexistente_no_saldo_retorna_404(conta_id):
    reset_database()
    assume(conta_id not in CONTAS_VALIDAS)

    resposta = requests.get(f"{BASE_URL}/saldo/{conta_id}")

    assert resposta.status_code == 404


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
def test_invariante_transferencia_aceita_conserva_soma_dos_saldos(origem, destino, valor):
    reset_database()
    assume(origem != destino)
    assume(float(valor) <= SALDOS_INICIAIS[origem])

    saldo_origem_antes = saldo(origem)
    saldo_destino_antes = saldo(destino)
    soma_antes = saldo_origem_antes + saldo_destino_antes

    resposta = requests.post(
        f"{BASE_URL}/transferencia",
        json={"origem": origem, "destino": destino, "valor": float(valor)},
    )

    assert resposta.status_code == 200

    saldo_origem_depois = saldo(origem)
    saldo_destino_depois = saldo(destino)
    soma_depois = saldo_origem_depois + saldo_destino_depois

    assert abs(soma_antes - soma_depois) < 0.000001
