import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests, json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from data_loader import load_data, formatar_dados_para_llm
from analysis import analisar_empresa
from feature_engineering import aplicar_classificacao

# ──────────────────────────────────────────────
# PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Adam · Agente Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d1117; }
.block-container { padding-top: 20px !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(160deg,#0d1117,#161b22);
    border-right: 1px solid #21262d;
}
[data-testid="stSidebar"] * { color: #e6edf3 !important; }

.adam-header {
    background: linear-gradient(135deg,#0d1117 0%,#1a1f2e 50%,#0d1117 100%);
    border: 1px solid #21262d; border-radius:16px;
    padding:24px 32px; margin-bottom:20px;
    display:flex; align-items:center; gap:18px;
}
.adam-title { font-family:'DM Serif Display',serif; font-size:30px; color:#e6edf3; margin:0; }
.adam-sub   { font-size:13px; color:#7d8590; margin:4px 0 0; }

.metric-card {
    background:#161b22; border:1px solid #21262d; border-radius:12px;
    padding:18px; text-align:center;
}
.metric-label { font-size:10px; text-transform:uppercase; letter-spacing:1px; color:#7d8590; margin-bottom:6px; }
.metric-value { font-family:'DM Serif Display',serif; font-size:26px; color:#e6edf3; }
.metric-sub   { font-size:11px; margin-top:4px; }

.badge { display:inline-block; padding:4px 14px; border-radius:20px; font-size:12px; font-weight:600; letter-spacing:.5px; }
.b-red  { background:#3d1a1a; border:1px solid #f85149; color:#ff6b6b; }
.b-yel  { background:#3d2d1a; border:1px solid #d29922; color:#e3b341; }
.b-blu  { background:#1a2d3d; border:1px solid #388bfd; color:#79c0ff; }
.b-grn  { background:#1a2e1a; border:1px solid #2ea043; color:#3fb950; }

.alert-item {
    background:#2e1a00; border:1px solid #d29922;
    border-left:4px solid #d29922; border-radius:8px;
    padding:10px 14px; margin:6px 0; font-size:13px; color:#e3b341;
}

.section-title {
    font-family:'DM Serif Display',serif; font-size:17px; color:#e6edf3;
    margin:22px 0 12px; padding-bottom:8px; border-bottom:1px solid #21262d;
}

/* chat */
.msg-user {
    background:#1f6feb22; border:1px solid #1f6feb44;
    border-radius:12px 12px 4px 12px;
    padding:12px 16px; margin:8px 0 8px auto;
    color:#e6edf3; max-width:85%; width:fit-content; margin-left:auto;
}
.msg-adam {
    background:#161b22; border:1px solid #21262d;
    border-radius:12px 12px 12px 4px;
    padding:14px 18px; margin:8px 0; color:#c9d1d9; line-height:1.65;
}
.msg-adam-label {
    font-size:10px; color:#388bfd; font-weight:700;
    text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px;
}

/* status */
.dot-online  { color:#3fb950; }
.dot-offline { color:#ff6b6b; }

/* inputs / buttons */
.stTextInput>div>div>input {
    background:#0d1117 !important; border:1px solid #21262d !important;
    color:#e6edf3 !important; border-radius:10px !important;
}
.stTextInput>div>div>input:focus {
    border-color:#388bfd !important;
    box-shadow:0 0 0 3px #388bfd22 !important;
}
.stButton>button {
    background:linear-gradient(135deg,#238636,#2ea043) !important;
    color:#fff !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important;
}
.stButton>button:hover { filter:brightness(1.15); transform:translateY(-1px); }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# OLLAMA
# ──────────────────────────────────────────────
OLLAMA_BASE = "http://localhost:11434"
DEFAULT_MODEL = "llama3.2"

def checar_ollama():
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=2)
        if r.status_code == 200:
            modelos = [m["name"] for m in r.json().get("models", [])]
            return True, modelos
    except Exception:
        pass
    return False, []

def stream_ollama(messages: list, model: str):
    """
    Faz streaming do Ollama e retorna um generator de tokens.
    """
    payload = {"model": model, "messages": messages, "stream": True}
    try:
        with requests.post(
            f"{OLLAMA_BASE}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        ) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("message", {}).get("content", "")
                    if token:
                        yield token
                    if data.get("done"):
                        break
    except requests.exceptions.ConnectionError:
        yield (
            "\n\n⚠️ **Ollama offline.** Inicie com:\n"
            "```\nollama serve\n```\n"
            "E instale um modelo:\n```\nollama pull llama3.2\n```"
        )
    except Exception as e:
        yield f"\n\n⚠️ Erro ao chamar Ollama: {e}"

def montar_mensagens(historico: list, contexto: str, pergunta: str) -> list:
    """
    Monta o array de mensagens para o Ollama:
    system prompt + histórico + nova pergunta com contexto embutido.
    """
    system = f"""Você é Adam, um consultor financeiro especializado em análise preditiva de Fluxo de Caixa Livre (FCF).

Seu papel é:
- Analisar os dados financeiros fornecidos abaixo
- Responder perguntas sobre a situação financeira da empresa
- Interpretar indicadores e tendências
- Fazer previsões com base nos dados históricos (projeção linear já está calculada)
- Explicar conceitos financeiros de forma didática, com metáforas simples
- Alertar riscos antes que se tornem crises
- Ser consultivo, preventivo e educativo

REGRAS ABSOLUTAS:
1. Baseie TODA resposta exclusivamente nos dados abaixo — nunca invente números
2. Se os dados forem insuficientes para responder, diga claramente
3. Nunca prometa retorno garantido ou certeza sobre o futuro
4. Nunca forneça dados bancários, senhas ou informações confidenciais
5. Se a pergunta estiver fora do escopo financeiro, redirecione educadamente
6. Estruture a resposta com: 📌 Diagnóstico → 📖 Explicação → ✅ Ação recomendada
7. Use metáforas do cotidiano para explicar conceitos técnicos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DADOS FINANCEIROS DA EMPRESA SELECIONADA:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{contexto}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    msgs = [{"role": "system", "content": system}]

    # Histórico anterior (sem o contexto, para não repetir)
    for m in historico:
        msgs.append({"role": m["role"], "content": m["content"]})

    # Nova mensagem do usuário
    msgs.append({"role": "user", "content": pergunta})
    return msgs

# ──────────────────────────────────────────────
# DADOS
# ──────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    return load_data()

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    df = carregar_dados()
    empresas = sorted(df["act_symbol"].unique().tolist())
    empresa_sel = st.selectbox("🏢 Empresa analisada", empresas)

    st.markdown("---")

    ollama_ok, modelos_disp = checar_ollama()
    if ollama_ok:
        st.markdown('<span style="color:#3fb950">● Ollama online</span>', unsafe_allow_html=True)
        modelo_sel = st.selectbox(
            "🤖 Modelo LLM",
            modelos_disp if modelos_disp else [DEFAULT_MODEL],
            index=0,
        )
    else:
        st.markdown('<span style="color:#ff6b6b">● Ollama offline</span>', unsafe_allow_html=True)
        modelo_sel = DEFAULT_MODEL
        st.caption("Para ativar:\n```\nollama serve\nollama pull llama3.2\n```")

    st.markdown("---")
    st.markdown("### 💬 Perguntas rápidas")
    sugestoes = [
        "Qual o risco financeiro atual da empresa?",
        "Como foi a evolução do FCF nos últimos anos?",
        "Quais são as projeções para os próximos 3 anos?",
        "Quais alertas você identifica nos dados?",
        "Compare os períodos de crescimento e queda",
        "O que explica a volatilidade do fluxo de caixa?",
        "Quais ações preventivas você recomenda?",
        "O que significa FCF negativo para esta empresa?",
    ]
    for s in sugestoes:
        if st.button(s, key=f"s_{s[:15]}", use_container_width=True):
            st.session_state["input_rapido"] = s

    st.markdown("---")
    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.pop("historico", None)
        st.rerun()

    st.markdown("---")
    st.caption("Adam v2.0 · DIO Lab · 2025\nPowered by Ollama + LLaMA")

# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("""
<div class="adam-header">
  <div style="font-size:46px">🤖</div>
  <div>
    <p class="adam-title">Adam</p>
    <p class="adam-sub">Agente de Análise Preditiva de Fluxo de Caixa · Powered by Ollama</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# PAINEL DE MÉTRICAS
# ──────────────────────────────────────────────
resultado = analisar_empresa(df, empresa_sel)

if "erro" not in resultado:
    metricas    = resultado["metricas"]
    alertas     = resultado["alertas"]
    classif     = resultado["classificacao"]

    badge_cfg = {
        "ALTO RISCO":      ("b-red",  "🔴 ALTO RISCO"),
        "EM DETERIORAÇÃO": ("b-yel",  "🟡 EM DETERIORAÇÃO"),
        "INSTÁVEL":        ("b-blu",  "🔵 INSTÁVEL"),
        "SAUDÁVEL":        ("b-grn",  "🟢 SAUDÁVEL"),
    }
    bcls, blbl = badge_cfg.get(classif, ("b-blu", classif))

    st.markdown(f'<p class="section-title">📊 Painel · {empresa_sel}</p>', unsafe_allow_html=True)
    st.markdown(f'<span class="badge {bcls}">{blbl}</span><br><br>', unsafe_allow_html=True)

    def fmt(v): return f"${v/1e6:.1f}M"
    def cor(v): return "color:#3fb950" if v >= 0 else "color:#ff6b6b"

    c1, c2, c3, c4, c5 = st.columns(5)
    cards = [
        (c1, "FCF Médio",            metricas["fcf_medio"],          None),
        (c2, "Último FCF",           metricas["ultimo_fcf"],         "▲" if metricas["ultimo_fcf"] >= 0 else "▼"),
        (c3, "Tendência / período",  metricas["tendencia_fcf"],      "▲ Positiva" if metricas["tendencia_fcf"] >= 0 else "▼ Negativa"),
        (c4, "Volatilidade",         metricas["volatilidade_fcf"],   None),
        (c5, "% Períodos Negativos", None,                           None),
    ]
    for col, lbl, val, sub in cards:
        with col:
            if lbl == "% Períodos Negativos":
                pct = metricas["proporcao_negativos"]
                c = "color:#ff6b6b" if pct > 0.5 else "color:#3fb950"
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-label">{lbl}</div>
                  <div class="metric-value" style="{c}">{pct:.0%}</div>
                </div>""", unsafe_allow_html=True)
            else:
                sub_html = f'<div class="metric-sub" style="{cor(val)}">{sub}</div>' if sub else ""
                st.markdown(f"""
                <div class="metric-card">
                  <div class="metric-label">{lbl}</div>
                  <div class="metric-value">{fmt(val)}</div>
                  {sub_html}
                </div>""", unsafe_allow_html=True)

    # Gráfico FCF
    st.markdown("<br>", unsafe_allow_html=True)
    df_emp = df[df["act_symbol"] == empresa_sel].sort_values("date")
    anos   = df_emp["date"].dt.strftime("%Y")
    fcf    = df_emp["free_cash_flow"]
    cores  = ["#3fb950" if v >= 0 else "#f85149" for v in fcf]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=anos, y=fcf/1e6, marker_color=cores, name="FCF anual",
        hovertemplate="Ano: %{x}<br>FCF: $%{y:.2f}M<extra></extra>",
    ))
    if "fcf_rolling_mean" in df_emp.columns:
        fig.add_trace(go.Scatter(
            x=anos, y=df_emp["fcf_rolling_mean"]/1e6,
            mode="lines+markers",
            line=dict(color="#388bfd", width=2, dash="dash"),
            name="Média móvel (3p)",
        ))

    # Projeção simples visível no gráfico
    df_ult5 = df_emp.tail(5)
    if len(df_ult5) >= 3:
        x_num = np.arange(len(df_ult5))
        coef  = np.polyfit(x_num, df_ult5["free_cash_flow"].values, 1)
        n     = len(df_ult5)
        ultimo_ano = df_emp["date"].dt.year.max()
        proj_anos  = [str(ultimo_ano + i) for i in range(1, 4)]
        proj_vals  = [np.polyval(coef, n + i - 1)/1e6 for i in range(1, 4)]
        fig.add_trace(go.Scatter(
            x=proj_anos, y=proj_vals,
            mode="lines+markers",
            line=dict(color="#d29922", width=2, dash="dot"),
            marker=dict(symbol="diamond", size=8),
            name="Projeção (linear)",
        ))

    fig.add_hline(y=0, line_color="#7d8590", line_dash="dot", line_width=1)
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#161b22",
        font=dict(family="DM Sans", color="#c9d1d9"),
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", y=1.08),
        xaxis=dict(gridcolor="#21262d"),
        yaxis=dict(gridcolor="#21262d", title="FCF (Milhões USD)"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # Alertas
    if alertas:
        st.markdown('<p class="section-title">⚠️ Alertas Ativos</p>', unsafe_allow_html=True)
        for a in alertas:
            st.markdown(f'<div class="alert-item">⚠️ {a}</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CHAT PRINCIPAL
# ──────────────────────────────────────────────
st.markdown('<p class="section-title">💬 Converse com o Adam</p>', unsafe_allow_html=True)

if "historico" not in st.session_state:
    st.session_state["historico"] = []

# Exibir histórico
for msg in st.session_state["historico"]:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user">{msg["content"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        conteudo = msg["content"].replace("\n", "<br>")
        st.markdown(
            f'<div class="msg-adam"><div class="msg-adam-label">🤖 Adam</div>{conteudo}</div>',
            unsafe_allow_html=True,
        )

# Input
col_i, col_b = st.columns([5, 1])
input_val = st.session_state.pop("input_rapido", "")

with col_i:
    pergunta = st.text_input(
        "pergunta",
        value=input_val,
        placeholder="Faça uma pergunta sobre a situação financeira da empresa...",
        label_visibility="collapsed",
        key="chat_input",
    )
with col_b:
    enviar = st.button("Enviar ▶", use_container_width=True)

# Processar
if enviar and pergunta.strip():
    # Mostra a mensagem do usuário imediatamente
    st.markdown(
        f'<div class="msg-user">{pergunta}</div>',
        unsafe_allow_html=True,
    )

    # Prepara contexto com dados reais da empresa
    contexto = formatar_dados_para_llm(df, empresa_sel)

    # Monta histórico sem repetir o contexto em cada mensagem
    mensagens_llm = montar_mensagens(
        st.session_state["historico"], contexto, pergunta
    )

    # Streaming da resposta
    st.markdown('<div class="msg-adam"><div class="msg-adam-label">🤖 Adam</div>', unsafe_allow_html=True)
    resposta_container = st.empty()
    resposta_completa  = ""

    with st.spinner(""):
        for token in stream_ollama(mensagens_llm, modelo_sel):
            resposta_completa += token
            resposta_container.markdown(resposta_completa + "▌")

    resposta_container.markdown(resposta_completa)
    st.markdown("</div>", unsafe_allow_html=True)

    # Salva no histórico
    st.session_state["historico"].append({"role": "user",      "content": pergunta})
    st.session_state["historico"].append({"role": "assistant", "content": resposta_completa})

    st.rerun()
