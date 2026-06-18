#!/usr/bin/env python3
"""
gera_matriz.py
--------------
Le o report.xml gerado pelo pytest (--junit-xml=report.xml) e produz
uma tabela Markdown de matriz de rastreabilidade:
    Requisito <-> Caso de Teste <-> Status de Execucao

Uso:
    python scripts/gera_matriz.py > matriz_rastreabilidade.md
"""

import xml.etree.ElementTree as ET
import sys
import os

# ---------------------------------------------------------------------------
# 1. MAPEAMENTO: substring do nome do teste -> (ID ISO 29119-3, Requisito, Artefato)
# ---------------------------------------------------------------------------
RASTREABILIDADE = {
    "test_saldo_conta_existente":          ("TC-01", "REQ-01: GET /saldo retorna saldo correto",         "test_ia_gerado.py"),
    "test_saldo_conta_inexistente":        ("TC-01", "REQ-01: GET /saldo retorna 404 para conta invalida","test_ia_gerado.py"),
    "test_transferencia_valida":           ("TC-01", "REQ-01: POST /transferencia bem-sucedida",         "test_ia_gerado.py"),
    "test_transferencia_saldo_insuficiente":("TC-03","REQ-03: Rejeicao com HTTP 422 saldo insuficiente", "test_ia_gerado.py"),
    "test_transferencia_conta_inexistente":("TC-01", "REQ-01: POST /transferencia conta inexistente",    "test_ia_gerado.py"),
    "test_saldo_igual_valor":              ("TC-03", "REQ-03: Transferencia exata do saldo disponivel",  "test_ia_gerado.py"),
    "test_invariante":                     ("TC-02", "REQ-02: Conservacao de valor em transferencias",   "test_hypothesis.py"),
    "test_propriedade":                    ("TC-02", "REQ-02: Property-based invariante bancaria",       "test_hypothesis.py"),
    "test_saldo_nunca_negativo":           ("TC-02", "REQ-02: Saldo nunca negativo apos transferencia",  "test_hypothesis.py"),
    "test_valor_positivo":                 ("TC-02", "REQ-02: Valor transferido sempre positivo",        "test_hypothesis.py"),
    "test_matar_mutante":                  ("TC-03", "REQ-03: Deteccao de mutante sobrevivente",         "test_melhorado.py"),
    "test_melhorado":                      ("TC-03", "REQ-03: Cobertura de mutante via caixa branca",    "test_melhorado.py"),
    "test_422":                            ("TC-03", "REQ-03: HTTP 422 mensagem exata",                  "test_melhorado.py"),
    "sistema_deve":                        ("TC-04", "REQ-04: Inicializacao segura do banco (BDD)",      "transferencia.feature"),
    "transferencia":                       ("TC-04", "REQ-04: Cenario BDD de transferencia",             "transferencia.feature"),
    "inicializacao":                       ("TC-04", "REQ-04: Inicializacao segura do banco de dados",   "transferencia.feature"),
}

# ---------------------------------------------------------------------------
# 2. LEITURA DO REPORT.XML
# ---------------------------------------------------------------------------
def encontrar_report():
    """Localiza o report.xml relativo a este script ou na raiz do projeto."""
    candidatos = [
        os.path.join(os.path.dirname(__file__), "..", "report.xml"),
        os.path.join(os.path.dirname(__file__), "report.xml"),
        "report.xml",
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c
    return None

def ler_resultados_pytest(caminho_xml):
    """Retorna dict {nome_do_teste: status} a partir do report.xml."""
    tree = ET.parse(caminho_xml)
    root = tree.getroot()
    resultados = {}
    for testcase in root.iter("testcase"):
        nome = testcase.get("name", "desconhecido")
        classname = testcase.get("classname", "")
        chave = f"{classname}::{nome}" if classname else nome
        if testcase.find("failure") is not None or testcase.find("error") is not None:
            status = "FALHOU"
        elif testcase.find("skipped") is not None:
            status = "PULADO"
        else:
            status = "PASSOU"
        resultados[chave] = status
    return resultados

# ---------------------------------------------------------------------------
# 3. GERACAO DA TABELA MARKDOWN
# ---------------------------------------------------------------------------
def mapear(nome_completo):
    """Tenta mapear um nome de teste para os dados de rastreabilidade."""
    nome_lower = nome_completo.lower()
    for chave, dados in RASTREABILIDADE.items():
        if chave in nome_lower:
            return dados
    return None

def gerar_matriz(resultados):
    emoji = {"PASSOU": "PASSOU", "FALHOU": "FALHOU", "PULADO": "PULADO"}
    linhas = []
    linhas.append("# Matriz de Rastreabilidade — Internet Banking")
    linhas.append("")
    linhas.append("Gerada automaticamente pelo pipeline GitHub Actions.")
    linhas.append("")
    linhas.append("| ID (ISO 29119-3) | Requisito Rastreado | Artefato | Teste (pytest) | Status |")
    linhas.append("|---|---|---|---|---|")

    rastreados = 0
    for nome, status in sorted(resultados.items()):
        mapeamento = mapear(nome)
        if mapeamento:
            tc_id, requisito, artefato = mapeamento
            rastreados += 1
        else:
            tc_id, requisito, artefato = "—", "*(sem rastreabilidade mapeada)*", "—"
        # Nome curto para exibicao
        nome_curto = nome.split("::")[-1] if "::" in nome else nome
        linhas.append(f"| {tc_id} | {requisito} | `{artefato}` | `{nome_curto}` | {status} |")

    linhas.append("")
    linhas.append(f"**Total de testes no report.xml:** {len(resultados)}")
    linhas.append(f"**Testes com rastreabilidade ISO 29119-3:** {rastreados}")
    linhas.append("")
    linhas.append("*Matriz gerada a cada commit pelo CI — auditoria humana necessaria para validar completude.*")
    return "\n".join(linhas)

# ---------------------------------------------------------------------------
# 4. PONTO DE ENTRADA
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    caminho = encontrar_report()
    if not caminho:
        print("ERRO: report.xml nao encontrado. Execute: pytest --junit-xml=report.xml", file=sys.stderr)
        sys.exit(1)
    resultados = ler_resultados_pytest(caminho)
    print(gerar_matriz(resultados))
