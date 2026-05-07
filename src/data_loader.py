import pandas as pd
import numpy as np


def load_data():
    df = pd.read_csv('data/cash_flow_statement.csv', sep=";")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df[df["period"] == "Year"]
    df = df.drop_duplicates(subset=["act_symbol", "date"])
    df = df.sort_values(["act_symbol", "date"])

    df["free_cash_flow"] = (
        df["net_cash_from_operating_activities"] + df["property_and_equipment"]
    )
    df["fcf_change"] = df.groupby("act_symbol")["free_cash_flow"].diff()
    df["fcf_rolling_mean"] = (
        df.groupby("act_symbol")["free_cash_flow"]
        .rolling(window=3, min_periods=2)
        .mean()
        .reset_index(0, drop=True)
    )
    df["fcf_negative"] = df["free_cash_flow"] < 0

    return df


def validate_data(df):
    print("\n===INFO===")
    print(df.info())
    print("\n===NULOS===")
    print(df.isnull().sum())
    print("\n===DUPLICADOS===")
    print(df.duplicated().sum())
    print("\n===AMOSTRA===")
    print(df.head())


def formatar_dados_para_llm(df, empresa: str) -> str:
    """
    Formata os dados financeiros da empresa de forma clara e estruturada
    para ser enviado como contexto ao LLM.
    """
    df_emp = df[df["act_symbol"] == empresa].copy()
    if df_emp.empty:
        return f"Nenhum dado encontrado para a empresa '{empresa}'."

    df_emp = df_emp.sort_values("date")

    def fmt(v):
        if pd.isna(v):
            return "N/A"
        m = v / 1_000_000
        sinal = "+" if m >= 0 else ""
        return f"{sinal}{m:.2f}M"

    linhas = []
    linhas.append(f"EMPRESA: {empresa}")
    linhas.append(f"PERÍODOS DISPONÍVEIS: {len(df_emp)} anos ({df_emp['date'].dt.year.min()} a {df_emp['date'].dt.year.max()})")
    linhas.append("")
    linhas.append("HISTÓRICO ANUAL (valores em USD):")
    linhas.append("-" * 70)

    for _, row in df_emp.iterrows():
        ano = row["date"].strftime("%Y")
        fcf = fmt(row["free_cash_flow"])
        op = fmt(row["net_cash_from_operating_activities"])
        fin = fmt(row.get("net_cash_from_financing_activities", np.nan))
        ni = fmt(row.get("net_income", np.nan))
        neg = " ⚠️ FCF NEGATIVO" if row["fcf_negative"] else ""
        linhas.append(
            f"  {ano} | FCF: {fcf:>10s} | Op. Cash: {op:>10s} | "
            f"Financiamento: {fin:>10s} | Net Income: {ni:>10s}{neg}"
        )

    linhas.append("")

    # Estatísticas resumidas
    fcf_serie = df_emp["free_cash_flow"]
    n_neg = df_emp["fcf_negative"].sum()
    pct_neg = n_neg / len(df_emp)
    tend = df_emp["fcf_change"].mean()
    fcf_ult3 = df_emp.tail(3)["free_cash_flow"].tolist()

    linhas.append("RESUMO ESTATÍSTICO:")
    linhas.append(f"  FCF médio histórico   : {fmt(fcf_serie.mean())}")
    linhas.append(f"  FCF último período    : {fmt(fcf_serie.iloc[-1])}")
    linhas.append(f"  Tendência (variação/ano): {fmt(tend)}")
    linhas.append(f"  Volatilidade (desvio) : {fmt(fcf_serie.std())}")
    linhas.append(f"  Períodos com FCF negativo: {n_neg}/{len(df_emp)} ({pct_neg:.0%})")
    linhas.append(f"  FCF últimos 3 períodos: {', '.join(fmt(v) for v in fcf_ult3)}")

    # Projeção simples por tendência linear
    linhas.append("")
    linhas.append("PROJEÇÃO BASEADA EM TENDÊNCIA LINEAR (últimos 5 anos):")
    df_ult5 = df_emp.tail(5).copy()
    if len(df_ult5) >= 3:
        x = np.arange(len(df_ult5))
        y = df_ult5["free_cash_flow"].values
        coef = np.polyfit(x, y, 1)
        proj1 = np.polyval(coef, len(df_ult5))
        proj2 = np.polyval(coef, len(df_ult5) + 1)
        proj3 = np.polyval(coef, len(df_ult5) + 2)
        ultimo_ano = df_emp["date"].dt.year.max()
        linhas.append(f"  {ultimo_ano+1}: {fmt(proj1)} (projeção)")
        linhas.append(f"  {ultimo_ano+2}: {fmt(proj2)} (projeção)")
        linhas.append(f"  {ultimo_ano+3}: {fmt(proj3)} (projeção)")
        linhas.append("  ⚠️ Projeções são estimativas lineares — não garantem o futuro real.")

    return "\n".join(linhas)


if __name__ == "__main__":
    df = load_data()
    validate_data(df)
    print("\n" + "=" * 70)
    print(formatar_dados_para_llm(df, "ORMP"))
