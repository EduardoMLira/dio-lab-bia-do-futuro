"""
main.py — Execução do Agente Adam via terminal
Útil para testar o agente sem precisar da interface Streamlit

Uso:
  python main.py          # roda demonstração completa
  python main.py validar  # valida os dados carregados
  python main.py chat     # modo interativo no terminal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_data, validate_data
from analysis import (
    analisar_empresa,
    analisar_todas_empresas,
    comparar_empresas,
    gerar_resumo_executivo,
)
from agent import responder
from feature_engineering import aplicar_classificacao


def linha(char="─", n=60):
    print(char * n)


def demo_analise_completa(df):
    print("\n")
    linha("═")
    print("  📊  ADAM — AGENTE DE ANÁLISE PREDITIVA DE FCF")
    linha("═")

    print("\n📁 DADOS CARREGADOS:")
    empresas = df["act_symbol"].unique()
    print(f"   Empresas disponíveis: {', '.join(empresas)}")
    print(f"   Total de registros  : {len(df)}")
    print(f"   Período coberto     : {df['date'].min().year} – {df['date'].max().year}")

    linha()
    print("\n📊 CLASSIFICAÇÃO GERAL:")
    linha()
    ranking = aplicar_classificacao(df)
    icones = {"ALTO RISCO": "🔴", "EM DETERIORAÇÃO": "🟡", "INSTÁVEL": "🔵", "SAUDÁVEL": "🟢"}
    for _, row in ranking.iterrows():
        icone = icones.get(row["classificacao"], "⚪")
        print(f"   {icone}  {row['empresa']:6s}  —  {row['classificacao']}")

    linha()
    print("\n🔎 ANÁLISE DETALHADA POR EMPRESA:")
    for empresa in empresas:
        linha("─")
        resultado = analisar_empresa(df, empresa)
        print(gerar_resumo_executivo(resultado))

    linha()
    print("\n🔀 COMPARATIVO ENTRE EMPRESAS:")
    linha()
    comparacao = comparar_empresas(df, list(empresas))
    print(f"{'Empresa':8s} {'Classificação':16s} {'FCF Médio':>14s} {'Tendência':>12s} {'Volatilidade':>14s}")
    linha()
    for c in comparacao:
        print(
            f"{c['empresa']:8s} {c['classificacao']:16s}"
            f" ${c['fcf_medio']/1e6:>10.2f}M"
            f" ${c['tendencia_fcf']/1e6:>8.2f}M"
            f" ${c['volatilidade']/1e6:>10.2f}M"
        )


def demo_agente_interativo(df, empresa="ORMP"):
    print(f"\n")
    linha("═")
    print(f"  💬  SIMULAÇÃO DE CONVERSA — Empresa: {empresa}")
    linha("═")

    perguntas_demo = [
        "A empresa está correndo risco financeiro?",
        "Qual a previsão do tempo para amanhã?",
        "Como está o fluxo de caixa da empresa?",
    ]

    for pergunta in perguntas_demo:
        print(f"\n👤 Usuário:\n   {pergunta}")
        resposta = responder(pergunta, df, empresa)
        print(f"\n🤖 Adam:")
        for l in resposta.splitlines():
            print(f"   {l}")
        linha()


def modo_interativo(df):
    empresas = list(df["act_symbol"].unique())
    print("\n\n💬 MODO INTERATIVO — Digite 'sair' para encerrar")
    linha()
    print("Empresas disponíveis:", ", ".join(empresas))
    empresa = input("\nEscolha a empresa: ").strip().upper()
    if empresa not in empresas:
        print(f"Empresa '{empresa}' não encontrada. Usando {empresas[0]}.")
        empresa = empresas[0]

    print(f"\n🤖 Adam: Olá! Sou seu assistente de análise financeira.")
    print(f"   Vou monitorar o fluxo de caixa de {empresa}. Como posso ajudar?\n")

    while True:
        try:
            pergunta = input("👤 Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n🤖 Adam: Até logo!")
            break
        if not pergunta:
            continue
        if pergunta.lower() in ("sair", "exit", "quit"):
            print("🤖 Adam: Até logo!")
            break
        resposta = responder(pergunta, df, empresa)
        print(f"\n🤖 Adam:\n{resposta}\n")


if __name__ == "__main__":
    print("\n🔄 Carregando dados financeiros...")
    df = load_data()
    modo = sys.argv[1] if len(sys.argv) > 1 else "demo"

    if modo == "validar":
        validate_data(df)
    elif modo == "chat":
        modo_interativo(df)
    else:
        demo_analise_completa(df)
        demo_agente_interativo(df)
        print("\n💡 Dica: rode 'python main.py chat' para modo interativo")
        print("         ou 'streamlit run app.py' para a interface visual\n")
