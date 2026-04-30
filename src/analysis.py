from feature_engineering import (
    classificar_empresa,
    extrair_metricas_empresa
)
from alerts import gerar_alertas


def analisar_empresa(df, empresa):
    
    #Executa uma análise completa de uma única empresa
    

    df_empresa = df[df["act_symbol"] == empresa]

    if df_empresa.empty:
        return {
            "erro": f"Empresa '{empresa}' não encontrada nos dados."
        }

    # Garantir ordenação correta
    df_empresa = df_empresa.sort_values("date")

    # CLASSIFICAÇÃO

    classificacao = classificar_empresa(df_empresa)

    # MÉTRICAS

    metricas = extrair_metricas_empresa(df_empresa)

    # ALERTAS

    alertas = gerar_alertas(df_empresa)

    # RESULTADO FINAL

    return {
        "empresa": empresa,
        "classificacao": classificacao,
        "metricas": metricas,
        "alertas": alertas
    }


def analisar_todas_empresas(df):
    
    #Executa análise para todas as empresas do dataset
    

    resultados = []

    for empresa in df["act_symbol"].unique():
        resultado = analisar_empresa(df, empresa)
        resultados.append(resultado)

    return resultados


def comparar_empresas(df, lista_empresas):
    
    #Compara múltiplas empresas lado a lado
    
    comparacao = []

    for empresa in lista_empresas:
        resultado = analisar_empresa(df, empresa)

        if "erro" not in resultado:
            comparacao.append({
                "empresa": empresa,
                "classificacao": resultado["classificacao"],
                "fcf_medio": resultado["metricas"]["fcf_medio"],
                "tendencia_fcf": resultado["metricas"]["tendencia_fcf"],
                "volatilidade": resultado["metricas"]["volatilidade_fcf"]
            })

    return comparacao


def gerar_resumo_executivo(resultado):
    
    #Gera um resumo textual estruturado (base pro agente Adam)
    
    if "erro" in resultado:
        return resultado["erro"]

    empresa = resultado["empresa"]
    classificacao = resultado["classificacao"]
    metricas = resultado["metricas"]
    alertas = resultado["alertas"]

    resumo = f"""
Empresa: {empresa}

Classificação: {classificacao}

Principais Indicadores:
- FCF médio: {metricas['fcf_medio']:.2f}
- Último FCF: {metricas['ultimo_fcf']:.2f}
- Tendência do FCF: {metricas['tendencia_fcf']:.2f}
- Volatilidade: {metricas['volatilidade_fcf']:.2f}
- % períodos negativos: {metricas['proporcao_negativos']:.2%}

Alertas:
"""

    if alertas:
        for alerta in alertas:
            resumo += f"- {alerta}\n"
    else:
        resumo += "- Nenhum alerta relevante\n"

    return resumo.strip()