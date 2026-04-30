import pandas as pd

def load_data():
    df = pd.read_csv('data/cash_flow_statement.csv', sep=";")

    #converter datas
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    #filtrar apenas um tipo de período
    df = df[df["period"] == "Year"]

    #remover dados duplicados
    df = df.drop_duplicates()

    #ordenar para garantir cálculos corretos de tendência
    df = df.sort_values(["act_symbol", "date"])

    #criar Fluxo de caixa livre
    df["free_cash_flow"] = (
        df["net_cash_from_operating_activities"] + df["property_and_equipment"]
    )

    #variação do FCF
    df["fcf_change"] = df.groupby("act_symbol")["free_cash_flow"].diff()

    #média móvel(3 períodos)
    df["fcf_rolling_mean"] = (
        df.groupby("act_symbol")["free_cash_flow"]
        .rolling(window=3, min_periods=3)
        .mean()
        .reset_index(0, drop=True)
    )

    #flag de FCF negativo
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


if __name__ == "__main__":
    df = load_data()
    validate_data(df)