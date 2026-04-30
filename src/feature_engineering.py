import pandas as pd


def classificar_empresa(df_empresa):
    """
    Classifica a empresa com base no comportamento do FCF
    """

    fcf_medio = df_empresa["free_cash_flow"].mean()
    total_periodos = len(df_empresa)

    fcf_negativos = df_empresa["fcf_negative"].sum()
    proporcao_negativos = fcf_negativos / total_periodos

    ultimo_fcf = df_empresa["free_cash_flow"].iloc[-1]
    tendencia = df_empresa["fcf_change"].mean()

    # =========================
    # REGRAS DE NEGÓCIO
    # =========================

    if fcf_medio < 0 and proporcao_negativos > 0.6:
        return "ALTO RISCO"

    elif tendencia < 0:
        return "EM DETERIORAÇÃO"

    elif proporcao_negativos > 0.4:
        return "INSTÁVEL"

    else:
        return "SAUDÁVEL"


def aplicar_classificacao(df):
    """
    Aplica a classificação para todas as empresas
    """

    resultados = []

    for empresa, grupo in df.groupby("act_symbol"):
        status = classificar_empresa(grupo)

        resultados.append({
            "empresa": empresa,
            "classificacao": status,
            "fcf_medio": grupo["free_cash_flow"].mean(),
            "proporcao_negativos": grupo["fcf_negative"].mean()
        })

    return pd.DataFrame(resultados)


def extrair_metricas_empresa(df_empresa):
    """
    Retorna métricas úteis para o agente usar
    """

    return {
        "fcf_medio": df_empresa["free_cash_flow"].mean(),
        "ultimo_fcf": df_empresa["free_cash_flow"].iloc[-1],
        "tendencia_fcf": df_empresa["fcf_change"].mean(),
        "volatilidade_fcf": df_empresa["free_cash_flow"].std(),
        "proporcao_negativos": df_empresa["fcf_negative"].mean()
    }