# 🤖 Adam — Agente de Análise Preditiva de Fluxo de Caixa

> Agente financeiro inteligente desenvolvido como projeto do **DIO Lab — BIA do Futuro**.  
> Analisa demonstrações de fluxo de caixa, identifica riscos, faz projeções e responde perguntas em linguagem natural via LLM local (Ollama).

---

## 📌 Sobre o Projeto

**Adam** é um agente de IA consultivo especializado em análise preditiva de **Fluxo de Caixa Livre (FCF)**. Seu objetivo é ajudar gestores financeiros de pequenas e médias empresas a:

- Identificar riscos de caixa **antes** que se tornem crises
- Entender tendências financeiras com linguagem acessível
- Obter projeções baseadas em dados históricos reais
- Interagir em tempo real com um consultor financeiro virtual

O agente utiliza um **LLM local via Ollama** como cérebro principal: os dados financeiros da empresa são formatados e enviados como contexto para o modelo, que raciocina livremente sobre eles e responde qualquer pergunta do usuário com streaming em tempo real.

---

## 🏗️ Arquitetura

```
Usuário (Streamlit)
       │
       ▼
  app.py  ──────────────────────────────────────────────┐
       │                                                 │
       ├── data_loader.py                                │
       │   └── Carrega CSV, calcula FCF,                 │
       │       formata contexto + projeção linear        │
       │                                                 │
       ├── analysis.py + feature_engineering.py          │
       │   └── Classificação de risco, métricas,         │
       │       comparativo entre empresas                │
       │                                                 │
       ├── alerts.py                                     │
       │   └── Detecção de alertas automáticos           │
       │                                                 │
       └── Ollama (LLM local) ◄────────────────────────┘
           └── Recebe: system prompt + dados + histórico
               Retorna: resposta em streaming
```

### Fluxo de uma pergunta

```
1. Usuário digita pergunta
2. data_loader formata todos os dados da empresa selecionada
   (histórico ano a ano, estatísticas, projeção 3 anos)
3. app.py monta o payload: [system prompt + dados + histórico + pergunta]
4. Ollama recebe tudo e raciocina sobre os números reais
5. Resposta chega token por token (streaming em tempo real)
6. Histórico é mantido — o agente lembra o contexto da conversa
```

---

## 🗂️ Estrutura do Repositório

```
dio-lab-bia-do-futuro/
│
├── 📁 src/                          # Código-fonte
│   ├── app.py                       # Interface Streamlit + integração Ollama
│   ├── main.py                      # Execução via terminal (demo / chat / validar)
│   ├── agent.py                     # Lógica de intenções e respostas (fallback)
│   ├── data_loader.py               # Carregamento, transformação e formatação p/ LLM
│   ├── analysis.py                  # Análise completa por empresa
│   ├── feature_engineering.py       # Classificação de risco e métricas
│   ├── alerts.py                    # Geração de alertas financeiros
│   └── requirements.txt             # Dependências Python
│
├── 📁 data/
│   └── cash_flow_statement.csv      # Dataset: 3 empresas, 2012–2025
│
├── 📁 docs/
│   ├── 01-documentacao-agente.md    # Caso de uso, persona e arquitetura
│   ├── 02-base-conhecimento.md      # Estratégia de dados
│   ├── 03-prompts.md                # System prompt e exemplos de interação
│   ├── 04-metricas.md               # Avaliação e métricas de qualidade
│   └── 05-pitch.md                  # Roteiro do pitch
│
├── 📁 assets/                       # Materiais de apoio
├── 📁 examples/                     # Referências e exemplos
└── README.md
```

---

## ⚙️ Pré-requisitos

| Ferramenta | Versão mínima | Descrição |
|------------|---------------|-----------|
| Python     | 3.10+         | Linguagem principal |
| Ollama     | qualquer      | Servidor LLM local |
| llama3.2   | —             | Modelo recomendado (ou outro de sua escolha) |

---

## 🚀 Como Rodar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/dio-lab-bia-do-futuro.git
cd dio-lab-bia-do-futuro
```

### 2. Instale as dependências Python

```bash
pip install -r src/requirements.txt
```

### 3. Instale e inicie o Ollama

```bash
# Instale o Ollama em: https://ollama.com/download

# Inicie o servidor (deixe rodando em um terminal)
ollama serve

# Baixe o modelo (só precisa fazer uma vez)
ollama pull llama3.2
```

> Você pode usar qualquer modelo disponível no Ollama. Para máquinas com menos memória, `llama3.2:1b` é uma alternativa mais leve.

### 4. Rode a interface

```bash
streamlit run src/app.py
```

Acesse em: **http://localhost:8501**

---

## 💻 Modos de Uso

### Interface Visual (recomendado)

```bash
streamlit run src/app.py
```

A interface oferece:
- **Dashboard** com métricas da empresa selecionada
- **Gráfico de FCF** histórico com média móvel e projeção
- **Alertas automáticos** detectados nos dados
- **Chat em tempo real** com o Adam via Ollama (streaming)
- **Perguntas rápidas** pré-definidas na sidebar
- **Seletor de modelo** — escolha entre os modelos instalados no Ollama

### Terminal — Demonstração

```bash
python src/main.py
```

Exibe classificação de risco de todas as empresas, análise detalhada por empresa, comparativo e simulação de conversa.

### Terminal — Chat Interativo

```bash
python src/main.py chat
```

Chat com o agente diretamente no terminal, sem a interface Streamlit. Útil para testar respostas rapidamente.

### Terminal — Validação dos Dados

```bash
python src/main.py validar
```

Inspeciona o dataset: tipos de dados, valores nulos, duplicatas e amostra.

---

## 📊 Dados Disponíveis

O dataset `cash_flow_statement.csv` contém demonstrações de fluxo de caixa de 3 empresas no período de **2012 a 2025**:

| Ticker | Classificação atual | Descrição |
|--------|---------------------|-----------|
| ORMP   | 🔴 ALTO RISCO        | FCF negativo em 94% dos períodos |
| UA     | 🟡 EM DETERIORAÇÃO   | FCF em queda nos últimos períodos |
| RGLD   | 🟢 SAUDÁVEL          | FCF positivo e crescente |

### Indicadores calculados automaticamente

- **Free Cash Flow (FCF)** = Caixa Operacional + Variação de Capex
- **Variação do FCF** (período a período)
- **Média móvel** (janela de 3 períodos)
- **Projeção linear** (próximos 3 anos com base nos últimos 5)
- **Classificação de risco**: ALTO RISCO / EM DETERIORAÇÃO / INSTÁVEL / SAUDÁVEL

---

## 🤖 O Agente Adam

### Persona

**Nome:** Adam  
**Tom:** Profissional, consultivo e didático  
**Especialidade:** Análise preditiva de Fluxo de Caixa Livre

### O que Adam consegue responder

- "A empresa está em risco financeiro?"
- "Como foi a evolução do FCF nos últimos anos?"
- "Quais são as projeções para os próximos 3 anos?"
- "Por que 2023 foi um ano ruim para esta empresa?"
- "O que significa FCF negativo na prática?"
- "Quais ações preventivas você recomenda?"
- "Compare os períodos de crescimento e queda"
- Qualquer pergunta relacionada aos dados financeiros disponíveis

### Estrutura padrão das respostas

```
📌 Diagnóstico     — O que está acontecendo
📖 Explicação      — Por que isso importa (com metáforas simples)
✅ Ação recomendada — O que fazer agora
```

### Segurança e anti-alucinação

- O LLM recebe **apenas os dados reais do CSV** como contexto
- Proibido inventar números ou prometer retorno garantido
- Perguntas fora do escopo são redirecionadas educadamente
- Dados sensíveis (bancários, senhas, contratos) são recusados
- Quando os dados são insuficientes, o agente informa claramente

---

## 📐 Classificação de Risco

| Classificação | Critério |
|---------------|----------|
| 🔴 ALTO RISCO | FCF médio negativo E mais de 60% dos períodos negativos |
| 🟡 EM DETERIORAÇÃO | Tendência de queda no FCF (variação média negativa) |
| 🔵 INSTÁVEL | Mais de 40% dos períodos com FCF negativo |
| 🟢 SAUDÁVEL | Nenhum dos critérios acima |

---

## 🧪 Testando o Agente

Cenários sugeridos para validação:

| Pergunta | Comportamento esperado |
|----------|------------------------|
| "A empresa está em risco?" | Diagnóstico com classificação e alertas |
| "Qual a previsão do tempo?" | Redireciona para escopo financeiro |
| "Me dê os dados bancários" | Recusa com explicação de limites |
| "O que é FCF negativo?" | Explicação didática com metáfora |
| "Quais as projeções para 2027?" | Usa a projeção linear calculada nos dados |

---

## 🔧 Personalização

### Trocar o modelo LLM

Na sidebar da interface, selecione qualquer modelo instalado no Ollama. Para instalar outros modelos:

```bash
ollama pull mistral
ollama pull gemma3
ollama pull phi4
```

### Adicionar novas empresas

Inclua os dados no arquivo `data/cash_flow_statement.csv` seguindo o mesmo formato (separador `;`, colunas iguais). O sistema detecta automaticamente todas as empresas no arquivo.

### Ajustar o system prompt

Edite a função `montar_mensagens()` em `src/app.py` para alterar o comportamento do agente, suas regras ou o formato das respostas.

---

## 📦 Dependências

```
streamlit>=1.35.0     # Interface web
pandas>=2.0.0         # Manipulação de dados
plotly>=5.18.0        # Gráficos interativos
requests>=2.31.0      # Comunicação com Ollama
python-dotenv>=1.0.0  # Variáveis de ambiente (opcional)
```

---

## 📄 Documentação Complementar

| Arquivo | Conteúdo |
|---------|----------|
| `docs/01-documentacao-agente.md` | Caso de uso, persona, arquitetura e segurança |
| `docs/02-base-conhecimento.md` | Estratégia de dados e integração |
| `docs/03-prompts.md` | System prompt, exemplos e edge cases |
| `docs/04-metricas.md` | Avaliação de qualidade e cenários de teste |
| `docs/05-pitch.md` | Roteiro para apresentação do projeto |

---

## 🎓 Contexto

Projeto desenvolvido no **DIO Lab — BIA do Futuro**, desafio de criação de um agente financeiro inteligente com IA Generativa.

O desafio propõe evoluir de chatbots reativos para agentes proativos — como a BIA do Bradesco —, capazes de antecipar necessidades, personalizar respostas e garantir segurança contra alucinações no setor financeiro.

---

> **Aviso:** Adam é uma ferramenta de apoio à decisão. Não substitui um contador, analista financeiro ou consultor especializado. Não realiza movimentações bancárias nem garante resultados futuros.