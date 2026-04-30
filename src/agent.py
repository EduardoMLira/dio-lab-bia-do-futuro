from analysis import analisar_empresa, gerar_resumo_executivo


def formatar_resposta(resultado):
    
    #Converte a análise em uma resposta no estilo do agente Adam
    

    if "erro" in resultado:
        return resultado["erro"]

    classificacao = resultado["classificacao"]
    metricas = resultado["metricas"]
    alertas = resultado["alertas"]

    # DIAGNÓSTICO

    diagnostico = f"A empresa está classificada como {classificacao}."

    # EXPLICAÇÃO

    explicacao = (
        f"O fluxo de caixa médio é de {metricas['fcf_medio']:.2f}, "
        f"com tendência de {metricas['tendencia_fcf']:.2f}. "
    )

    if metricas["proporcao_negativos"] > 0.5:
        explicacao += (
            "Grande parte dos períodos apresenta fluxo de caixa negativo, "
            "o que indica dificuldade em gerar caixa de forma consistente. "
        )

    explicacao += (
        "Isso funciona como uma pessoa que frequentemente gasta mais do que ganha, "
        "o que pode gerar dependência de crédito ou capital externo."
    )

    # AÇÃO

    acao = "Recomenda-se: "

    if classificacao == "ALTO RISCO":
        acao += "redução imediata de custos e revisão urgente da estrutura financeira."

    elif classificacao == "EM DETERIORAÇÃO":
        acao += "monitorar de perto os próximos períodos e ajustar despesas."

    elif classificacao == "INSTÁVEL":
        acao += "melhorar previsibilidade de caixa e reduzir volatilidade."

    else:
        acao += "manter a estratégia atual e buscar oportunidades de crescimento sustentável."

    # ALERTAS

    alerta_texto = ""
    if alertas:
        alerta_texto = "\n\nAlertas:\n"
        for alerta in alertas:
            alerta_texto += f"- {alerta}\n"

    # RESPOSTA FINAL

    resposta = f"""
Diagnóstico:
{diagnostico}

Explicação:
{explicacao}

Ação recomendada:
{acao}
{alerta_texto}
"""

    return resposta.strip()


def responder(pergunta, df, empresa):
    
    #Função principal do agente
    

    pergunta = pergunta.lower()

    #VALIDAÇÃO DE ESCOPO

    palavras_financeiras = [
        "fluxo", "caixa", "financeiro", "empresa",
        "risco", "lucro", "prejuízo"
    ]

    if not any(p in pergunta for p in palavras_financeiras):
        return (
            "Sou especializado em análise financeira e fluxo de caixa. "
            "Posso te ajudar com isso."
        )

    #ANÁLISE

    resultado = analisar_empresa(df, empresa)

    #FORMATAÇÃO

    resposta = formatar_resposta(resultado)

    return resposta