# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `cash_flow_satatement.csv` | CSV |  Base para análise preditiva de fluxo de caixa e identificação de risco financeiro |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

O arquivo original foi tratado e adaptado para atender ao objetivo do agente.

---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os dados são carregados inicialmente a partir do arquivo `cash_flow_statement.csv`, utilizando Python com `pandas`.

```python
import pandas as pd

cash_flow = pd.read_csv('data/cash_flow_statement.csv')
```

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados não ficam fixos dentro do system prompt.

O system prompt define apenas o comportamento do agente, sua persona, seu tom de voz e suas regras de segurança.

As informações financeiras são consultadas dinamicamente a partir do DataFrame carregado com `pandas` e enviadas como contexto antes da geração da resposta.

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```text
Empresa analisada:
- Ticker: ORMP
- Período analisado: últimos 3 trimestres

Indicadores financeiros:
- Operating Cash Flow: queda de 22%
- Capital Expenditure: aumento de 18%
- Free Cash Flow: negativo em 3 períodos consecutivos

Análise detectada:
- Risco elevado de deterioração de caixa
- Possível necessidade de capital externo no curto prazo

Objetivo do agente:
Explicar o cenário de forma didática, prever risco futuro e sugerir ações preventivas.