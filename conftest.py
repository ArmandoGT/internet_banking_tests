# conftest.py — Sprint 2 (autouse reset) + Sprint 4 (fixture client)
#
# IMPORTANTE: NÃO importar 'app' no topo do arquivo.
# O import lazy dentro da fixture evita que o Werkzeug debug reloader
# dispare durante a coleta dos testes pelo pytest.
#
# Fixture autouse: reseta o banco SQLite antes de cada teste.
# Garante independência dos testes (ISTQB CTFL v4.0, Cap. 6, p. 52-53).
#
# Fixture client: Flask test client — NÃO depende de servidor externo.
# Pré-requisito arquitetural do Sprint 4 para o mutmut funcionar
# (JIA; HARMAN, 2011, p. 651).

import os
import sqlite3
import pytest

DB_PATH = os.path.join(os.path.dirname(__file__), "banking.db")


@pytest.fixture(autouse=True)
def reset_sqlite_db_before_test():
    """
    Reseta o banco SQLite antes de cada teste.
    - Recria as tabelas `contas` e `transferencias` com os dados iniciais.
    - Fecha a conexão antes do `yield`.
    - Aplicada automaticamente a todos os testes (`autouse=True`).
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
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
    """)
    conn.commit()
    conn.close()
    yield


@pytest.fixture
def client():
    """
    Flask test client — Sprint 4 (test_flask_client.py) e Sprint 5 (BDD steps).
    Import lazy: evita inicialização do Werkzeug debug reloader na coleta.
    Aponta DATABASE para o mesmo banco gerenciado pelo reset autouse.
    """
    # Import AQUI (lazy) — não no topo do arquivo
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    flask_app.config["DATABASE"] = DB_PATH
    with flask_app.test_client() as c:
        yield c
