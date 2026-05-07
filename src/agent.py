import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analysis import analisar_empresa, gerar_resumo_executivo


# ──────────────────────────────────────────────
# CONSTANTES DE ESCOPO
# ──────────────────────────────────────────────

PALAVRAS_FINANCEIRAS = [
    "fluxo", "caixa", "financeiro", "empresa", "risco", "lucro", "prejuízo",
    "capital", "receita", "despesa", "custo", "investimento", "dívida",
    "saldo", "resultado", "indicador", "tendência", "deterioração",
    "instável", "saudável", "análise", "alerta", "demonstração",
    "fcf", "free cash flow", "operacional", "balanço", "ativo", "passivo",
    "endividamento", "rentabilidade", "liquidez", "solvência", "patrimônio",
    "situação financeira", "recomenda", "melhorar",
]

PERGUNTAS_SENSIVEIS = [
    "senha", "bancário", "conta corrente", "cpf", "cnpj", "dados pessoais",
    "cartão", "transferir", "pix", "boleto", "movimentar", "sacar",
    "contrato completo", "dados bancários",
]


# ──────────────────────────────────────────────
# FORMATAÇÃO DA RESPOSTA
# ──────────────────────────────────────────────

def formatar_resposta(resultado: dict) -> str:
    """Converte o resultado da análise em resposta estruturada do Adam."""
    if "erro" in resultado:
        return (
            "Não foi possível localizar dados suficientes para essa empresa. "
            "Verifique se o ticker está correto e tente novamente."
        )

    classificacao = resultado["classificacao"]
    metricas = resultado["metricas"]
    alertas = resultado["alertas"]

    # ── DIAGNÓSTICO ──────────────────────────────
    icone_map = {
        "ALTO RISCO":      "🔴",
        "EM DETERIORAÇÃO": "🟡",
        "INSTÁVEL":        "🔵",
        "SAUDÁVEL":        "🟢",
    }
    icone = icone_map.get(classificacao, "⚪")
    diagnostico = f"A empresa está classificada como **{icone} {classificacao}**."

    # ── EXPLICAÇÃO ───────────────────────────────
    fcf_medio = metricas["fcf_medio"]
    tendencia = metricas["tendencia_fcf"]
    proporcao_neg = metricas["proporcao_negativos"]

    explicacao = (
        f"O Fluxo de Caixa Livre médio é de ${fcf_medio/1e6:.2f}M, "
        f"com tendência de {'queda' if tendencia < 0 else 'alta'} "
        f"(${tendencia/1e6:.2f}M por período). "
    )

    if proporcao_neg > 0.6:
        explicacao += (
            f"Em {proporcao_neg:.0%} dos períodos o FCF foi negativo — "
            "como uma pessoa que frequentemente gasta mais do que ganha "
            "e precisa usar crédito para fechar o mês. "
            "Isso sinaliza dificuldade estrutural em gerar caixa."
        )
    elif proporcao_neg > 0.3:
        explicacao += (
            f"Em {proporcao_neg:.0%} dos períodos o FCF foi negativo, "
            "o que indica instabilidade e requer atenção."
        )
    else:
        explicacao += (
            "A maior parte dos períodos registrou FCF positivo, "
            "indicando que a empresa consegue gerar caixa de forma consistente."
        )

    # ── AÇÃO RECOMENDADA ──────────────────────────
    acoes = {
        "ALTO RISCO": (
            "Redução imediata de custos operacionais, renegociação de dívidas "
            "e avaliação urgente de fontes de capital externo. "
            "Considere acionar um especialista financeiro."
        ),
        "EM DETERIORAÇÃO": (
            "Monitorar de perto os próximos 2 períodos, identificar as causas "
            "da queda no FCF e ajustar o planejamento de despesas."
        ),
        "INSTÁVEL": (
            "Melhorar a previsibilidade do caixa, reduzir a volatilidade "
            "e criar uma reserva de emergência operacional."
        ),
        "SAUDÁVEL": (
            "Manter a estratégia atual, buscar oportunidades de crescimento "
            "sustentável e monitorar periodicamente os indicadores."
        ),
    }
    acao = acoes.get(classificacao, "Consulte um especialista financeiro.")

    # ── ALERTAS ───────────────────────────────────
    alerta_texto = ""
    if alertas:
        alerta_texto = "\n\n⚠️ **Alertas identificados:**\n"
        for alerta in alertas:
            alerta_texto += f"  • {alerta}\n"

    resposta = (
        f"📌 **Diagnóstico:**\n{diagnostico}\n\n"
        f"📖 **Explicação:**\n{explicacao}\n\n"
        f"✅ **Ação recomendada:**\n{acao}"
        f"{alerta_texto}"
    )
    return resposta.strip()


# ──────────────────────────────────────────────
# DETECÇÃO DE INTENÇÃO
# ──────────────────────────────────────────────

def detectar_intencao(pergunta: str) -> str:
    """Classifica a intenção da pergunta do usuário."""
    p = pergunta.lower()

    # 1. Sempre verificar sensível primeiro
    if any(s in p for s in PERGUNTAS_SENSIVEIS):
        return "sensivel"

    # 2. Verificar fora do escopo (nenhuma palavra financeira presente)
    if not any(w in p for w in PALAVRAS_FINANCEIRAS):
        return "fora_escopo"

    # 3. Intenções específicas dentro do domínio financeiro
    if any(w in p for w in ["alerta", "risco", "problema", "preocupante", "perigo", "atenção"]):
        return "alertas"

    if any(w in p for w in ["tendência", "tendencia", "histórico", "períodos", "evolução", "progressão", "últimos"]):
        return "tendencia"

    if any(w in p for w in ["comparar", "comparativo", "versus", "melhor", "pior", "diferença"]):
        return "comparacao"

    if any(w in p for w in ["o que", "significa", "explique", "como funciona", "definição", "o que é"]):
        return "educativo"

    return "analise_geral"


# ──────────────────────────────────────────────
# RESPOSTAS ESPECIALIZADAS
# ──────────────────────────────────────────────

def resposta_educativa(pergunta: str) -> str | None:
    """Responde perguntas educativas sobre conceitos financeiros."""
    p = pergunta.lower()

    if "fcf" in p or "fluxo de caixa livre" in p:
        return (
            "📖 **O que é Fluxo de Caixa Livre (FCF)?**\n\n"
            "É o dinheiro que sobra para a empresa após pagar todos os custos "
            "operacionais e os investimentos necessários para manter o negócio.\n\n"
            "💡 *Pense assim:* é como o seu salário menos todas as contas fixas "
            "(aluguel, luz, alimentação). O que sobra é o seu 'fluxo livre'.\n\n"
            "• **FCF positivo** → a empresa gera caixa, tem fôlego financeiro\n"
            "• **FCF negativo** → a empresa gasta mais do que gera, pode precisar de crédito\n"
            "• **FCF negativo consecutivo** → sinal de alerta, requer ação preventiva"
        )

    if "deterioração" in p:
        return (
            "📖 **O que significa 'em deterioração'?**\n\n"
            "A empresa ainda não está em crise, mas o fluxo de caixa está "
            "apresentando queda consistente — como um carro que ainda anda, "
            "mas está perdendo potência a cada quilômetro.\n\n"
            "✅ Agir agora é mais barato do que esperar a situação piorar."
        )

    if "alto risco" in p:
        return (
            "📖 **O que significa 'alto risco'?**\n\n"
            "A empresa apresenta FCF médio negativo e a maioria dos períodos "
            "com caixa no vermelho. É como alguém que, mês após mês, "
            "termina no limite do cheque especial.\n\n"
            "⚠️ Sem ação imediata, pode haver necessidade de capital externo urgente."
        )

    return None


def resposta_sem_contexto() -> str:
    return (
        "Para fazer uma análise responsável, preciso de dados financeiros da empresa — "
        "especialmente Fluxo de Caixa Livre, Fluxo Operacional e histórico recente.\n\n"
        "Sem esse contexto, qualquer recomendação seria apenas suposição, "
        "e isso não seria seguro para a tomada de decisão."
    )


# ──────────────────────────────────────────────
# FUNÇÃO PRINCIPAL DO AGENTE
# ──────────────────────────────────────────────

def responder(pergunta: str, df, empresa: str) -> str:
    """
    Função principal do agente Adam (modo regras — fallback sem LLM).
    Retorna uma resposta estruturada com base nos dados financeiros.
    """
    intencao = detectar_intencao(pergunta)

    # ── Pergunta sensível ──────────────────────
    if intencao == "sensivel":
        return (
            "Não posso fornecer informações sensíveis ou confidenciais.\n\n"
            "Minha função é apoiar análises financeiras com base em indicadores "
            "de desempenho como FCF, tendências e alertas de risco. "
            "Posso ajudar com isso?"
        )

    # ── Fora do escopo ─────────────────────────
    if intencao == "fora_escopo":
        return (
            "Sou especializado em análise financeira e fluxo de caixa. "
            "Sua pergunta parece estar fora desse escopo.\n\n"
            "Posso ajudar com: análise de risco financeiro, interpretação do FCF, "
            "alertas de deterioração, comparativos entre empresas e recomendações preventivas."
        )

    # ── Pergunta educativa ─────────────────────
    if intencao == "educativo":
        resp_edu = resposta_educativa(pergunta)
        if resp_edu:
            return resp_edu

    # ── Análise da empresa ─────────────────────
    resultado = analisar_empresa(df, empresa)

    if "erro" in resultado:
        return f"Empresa '{empresa}' não encontrada nos dados disponíveis."

    # Pergunta específica sobre alertas
    if intencao == "alertas":
        alertas = resultado["alertas"]
        if not alertas:
            return (
                f"✅ Nenhum alerta crítico identificado para **{empresa}** no momento.\n\n"
                "Continue monitorando os indicadores periodicamente."
            )
        resposta = f"⚠️ **Alertas identificados para {empresa}:**\n\n"
        for a in alertas:
            resposta += f"  • {a}\n"
        resposta += "\n✅ **Recomendação:** Revise os dados dos próximos períodos com atenção."
        return resposta

    # Pergunta sobre tendência
    if intencao == "tendencia":
        metricas = resultado["metricas"]
        tend = metricas["tendencia_fcf"]
        return (
            f"📈 **Tendência do FCF — {empresa}:**\n\n"
            f"A variação média por período é de **${tend/1e6:.2f}M**.\n\n"
            f"{'📉 Tendência de queda — atenção redobrada nos próximos períodos.' if tend < 0 else '📈 Tendência de alta — empresa evoluindo positivamente.'}\n\n"
            f"FCF médio histórico: **${metricas['fcf_medio']/1e6:.2f}M**\n"
            f"Último FCF registrado: **${metricas['ultimo_fcf']/1e6:.2f}M**"
        )

    # Análise geral / padrão
    return formatar_resposta(resultado)
