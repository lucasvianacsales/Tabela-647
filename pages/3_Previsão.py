import streamlit as st
import pandas as pd
import pickle

st.title("Previsão de Custo por m²")

# -----------------------------
# CARREGAR DADOS
# -----------------------------
df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

df["Mes"] = df["Mes"].astype(str).str.strip().str.capitalize()
df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")

with open("modelo.pkl", "rb") as f:
    modelo = pickle.load(f)

# -----------------------------
# CAMPOS DE ENTRADA
# -----------------------------
col1, col2 = st.columns(2)

uf = col1.selectbox(
    "Estado",
    sorted(df["UF"].dropna().unique())
)

padrao = col1.selectbox(
    "Padrão de Acabamento",
    sorted(df["Padrao_Acabamento"].dropna().unique())
)

meses_ordem = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

meses_presentes = [m for m in meses_ordem if m in df["Mes"].unique()]

mes = col2.selectbox(
    "Mês",
    meses_presentes
)

ano = col2.selectbox(
    "Ano",
    sorted(df["Ano"].dropna().astype(int).unique())
)

tipo = st.selectbox(
    "Tipo de Projeto",
    sorted(df["Tipo_Projeto"].dropna().unique())
)

# -----------------------------
# PREVISÃO
# -----------------------------
if st.button("Calcular custo estimado"):
    entrada = pd.DataFrame({
        "UF": [uf],
        "Padrao_Acabamento": [padrao],
        "Mes": [mes],
        "Ano": [ano],
        "Tipo_Projeto": [tipo]
    })

    previsao = modelo.predict(entrada)[0]

    st.success(f"Custo estimado: R$ {previsao:.2f} por m²")

    # -----------------------------
    # ALERTA: MÉDIA HISTÓRICA DO MESMO CENÁRIO
    # UF + Mês + Padrão + Tipo
    # -----------------------------
    filtro_ref = df[
        (df["UF"] == uf) &
        (df["Mes"] == mes) &
        (df["Padrao_Acabamento"] == padrao) &
        (df["Tipo_Projeto"] == tipo)
    ]

    if not filtro_ref.empty:
        media_referencia = filtro_ref["Valor_m2"].mean()
        minimo_historico = filtro_ref["Valor_m2"].min()
        maximo_historico = filtro_ref["Valor_m2"].max()

        diferenca_percentual = ((previsao - media_referencia) / media_referencia) * 100

        limite_superior = media_referencia * 1.10
        limite_inferior = media_referencia * 0.90

        st.write("### Referência histórica")
        st.write(f"**Média histórica (2021–2025):** R$ {media_referencia:.2f}/m²")
        st.write(f"**Menor valor observado:** R$ {minimo_historico:.2f}/m²")
        st.write(f"**Maior valor observado:** R$ {maximo_historico:.2f}/m²")

        if previsao > limite_superior:
            st.warning(
                f"🚨 Alerta: custo acima da média histórica para "
                f"{uf} / {mes} / {padrao} / {tipo}. "
                f"Variação: {diferenca_percentual:.1f}%"
            )
        elif previsao < limite_inferior:
            st.info(
                f"✅ Custo abaixo da média histórica para "
                f"{uf} / {mes} / {padrao} / {tipo}. "
                f"Variação: {diferenca_percentual:.1f}%"
            )
        else:
            st.caption(
                f"Custo dentro da faixa esperada para "
                f"{uf} / {mes} / {padrao} / {tipo}. "
                f"Variação: {diferenca_percentual:.1f}%"
            )
    else:
        st.caption("Não foi encontrada base histórica de comparação para esse cenário.")