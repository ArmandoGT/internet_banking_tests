# Matriz de Rastreabilidade ÔÇö Internet Banking

Gerada automaticamente pelo pipeline GitHub Actions.

| ID (ISO 29119-3) | Requisito Rastreado | Artefato | Teste (pytest) | Status |
|---|---|---|---|---|
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_cliente_deve_conseguir_consultar_saldo_depois_da_inicializa├º├úo` | PASSOU |
| TC-04 | REQ-04: Inicializacao segura do banco (BDD) | `transferencia.feature` | `test_sistema_deve_criar_as_contas_iniciais_ao_iniciar` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_extrato_conta_existente` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_extrato_conta_inexistente` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_saldo_alice` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_saldo_bob` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_saldo_carlos` | PASSOU |
| TC-01 | REQ-01: GET /saldo retorna 404 para conta invalida | `test_ia_gerado.py` | `test_saldo_conta_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_campos_ausentes` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_conta_destino_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_conta_origem_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_corpo_invalido` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_origem_destino_iguais` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_saldo_igual_valor` | PASSOU |
| TC-03 | REQ-03: Rejeicao com HTTP 422 saldo insuficiente | `test_ia_gerado.py` | `test_transferencia_saldo_insuficiente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_saldo_suficiente` | PASSOU |
| TC-01 | REQ-01: POST /transferencia bem-sucedida | `test_ia_gerado.py` | `test_transferencia_valida` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_valor_negativo` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_valor_zero` | PASSOU |
| TC-02 | REQ-02: Conservacao de valor em transferencias | `test_hypothesis.py` | `test_invariante_conta_inexistente_no_saldo_retorna_404` | PASSOU |
| TC-02 | REQ-02: Conservacao de valor em transferencias | `test_hypothesis.py` | `test_invariante_transferencia_aceita_conserva_soma_dos_saldos` | PASSOU |
| TC-02 | REQ-02: Conservacao de valor em transferencias | `test_hypothesis.py` | `test_invariante_valor_nao_positivo_sempre_rejeitado` | FALHOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_extrato_conta_inexistente` | PASSOU |
| ÔÇö | *(sem rastreabilidade mapeada)* | `ÔÇö` | `test_extrato_conta_origem_inexistente` | PASSOU |
| TC-01 | REQ-01: GET /saldo retorna saldo correto | `test_ia_gerado.py` | `test_saldo_conta_existente` | PASSOU |
| TC-01 | REQ-01: GET /saldo retorna 404 para conta invalida | `test_ia_gerado.py` | `test_saldo_conta_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_conta_destino_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_conta_origem_inexistente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_origem_destino_iguais` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_saldo_igual_valor` | PASSOU |
| TC-03 | REQ-03: Rejeicao com HTTP 422 saldo insuficiente | `test_ia_gerado.py` | `test_transferencia_saldo_insuficiente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_saldo_suficiente` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_valor_negativo` | PASSOU |
| TC-04 | REQ-04: Cenario BDD de transferencia | `transferencia.feature` | `test_transferencia_valor_zero` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_campo_saldo_atual_presente_em_saldo_insuficiente` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_conta_inexistente_transferencia_mensagem_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_extrato_campos_obrigatorios_alice` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_extrato_conta_inexistente_mensagem_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_extrato_reflete_transferencia_realizada` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_mensagem_campos_ausentes_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_mensagem_corpo_invalido_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_mensagem_origem_destino_iguais_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_mensagem_saldo_insuficiente_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_mensagem_valor_positivo_exata` | PASSOU |
| TC-01 | REQ-01: GET /saldo retorna 404 para conta invalida | `test_ia_gerado.py` | `test_saldo_conta_inexistente_mensagem_exata` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_saldo_retorna_campos_obrigatorios` | PASSOU |
| TC-03 | REQ-03: Cobertura de mutante via caixa branca | `test_melhorado.py` | `test_transferencia_retorna_campos_obrigatorios` | PASSOU |

**Total de testes no report.xml:** 47
**Testes com rastreabilidade ISO 29119-3:** 40

*Matriz gerada a cada commit pelo CI ÔÇö auditoria humana necessaria para validar completude.*
