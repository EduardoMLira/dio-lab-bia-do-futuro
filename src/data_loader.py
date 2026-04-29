import pandas as pd

cash_flow = pd.read_csv('data/cash_flow_statement.csv', sep=";")

cash_flow.info()