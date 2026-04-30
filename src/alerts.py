def gerar_alertas(df_empresa):
    
    #Gera alertas financeiros com base no comportamento do FCF
    
    alertas = []

    # garantir ordenação correta
    df_empresa = df_empresa.sort_values("date")

    #FCF negativo consecutivo

    if len(df_empresa) >= 3 and df_empresa["fcf_negative"].tail(3).all():
        alertas.append("Fluxo de caixa livre negativo por 3 períodos consecutivos")

    #Queda recente no FCF

    if df_empresa["fcf_change"].iloc[-1] < 0:
        alertas.append("Queda recente no fluxo de caixa")

    #Tendência negativa geral

    if df_empresa["fcf_change"].mean() < 0:
        alertas.append("Tendência geral de deterioração no fluxo de caixa")

    #Alta volatilidade (instabilidade)

    volatilidade = df_empresa["free_cash_flow"].std()

    if volatilidade > abs(df_empresa["free_cash_flow"].mean()):
        alertas.append("Alta volatilidade no fluxo de caixa (instabilidade)")

    #Queda acumulada forte

    if len(df_empresa) >= 3:
        fcf_inicio = df_empresa["free_cash_flow"].iloc[-3]
        fcf_final = df_empresa["free_cash_flow"].iloc[-1]

        if fcf_final < fcf_inicio:
            alertas.append("Queda acumulada nos últimos períodos")

    #Dependência de financiamento

    if "net_cash_from_financing_activities" in df_empresa.columns:
        financiamento = df_empresa["net_cash_from_financing_activities"].tail(3).sum()

        if financiamento > 0:
            alertas.append("Dependência recente de financiamento externo")

    return alertas