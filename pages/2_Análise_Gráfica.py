import streamlit as st
import pandas as pd
import plotly.express as px
from utils import filtros_laterais

st.set_page_config(
    page_title="Dashboard - Custo de Projetos m²",
    layout="wide"
)

st.title("Análise Gráfica")

# -----------------------------
# CARREGAR DATASET
# -----------------------------
df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

# -----------------------------
# APLICAR FILTROS LATERAIS
# -----------------------------
df_filtrado = filtros_laterais(df)

if not df_filtrado.empty:
    # -----------------------------
    # GRÁFICO 1: Evolução do valor médio por tipo de projeto
    # -----------------------------
    meses_ordem = ["Jan","Fev","Mar","Abr","Mai","Jun",
                   "Jul","Ago","Set","Out","Nov","Dez"]

    df_filtrado["Mes_Abr"] = df_filtrado["Mes"].str[:3].str.capitalize()
    df_filtrado["Mes_Abr"] = pd.Categorical(df_filtrado["Mes_Abr"], categories=meses_ordem, ordered=True)

    df_agrupado = df_filtrado.groupby(["Mes_Abr","Tipo_Projeto"])["Valor_m2"].mean().reset_index()

    fig_linha = px.line(
        df_agrupado,
        x="Mes_Abr", y="Valor_m2",
        color="Tipo_Projeto", markers=True,
        title="Evolução Média do Valor por m²",
        labels={"Valor_m2":"Valor m²","Mes_Abr":"Mês"}
    )
    st.plotly_chart(fig_linha, use_container_width=True)

    st.divider()  # separa os gráficos

    # -----------------------------
    # GRÁFICO 2: Comparação de custo médio por região com filtro interativo
    # -----------------------------
    st.subheader("Custo Médio por m² por Região")

    # Filtro de regiões com "Todos"
    regioes_disponiveis = [r for r in df_filtrado["Regiao"].unique().tolist() if r != "Todos"]
    regioes_opcoes = ["Todos"] + regioes_disponiveis

    regioes_selecionadas = st.multiselect(
        "Selecione as regiões para comparar",
        options=regioes_opcoes,
        default=["Todos"]
    )

    if "Todos" in regioes_selecionadas:
        regioes_selecionadas = regioes_disponiveis

    # Filtro de meses com "Todos"
    meses_disponiveis = [m for m in df_filtrado["Mes"].unique().tolist() if m != "Todos"]
    meses_opcoes = ["Todos"] + meses_disponiveis

    meses_selecionados = st.multiselect(
        "Selecione os meses",
        options=meses_opcoes,
        default=["Todos"]
    )

    if "Todos" in meses_selecionados:
        meses_selecionados = meses_disponiveis

    if regioes_selecionadas and meses_selecionados:
        # Filtrar dados por regiões e meses selecionados
        df_regiao = df_filtrado[
            (df_filtrado["Regiao"].isin(regioes_selecionadas)) &
            (df_filtrado["Mes"].isin(meses_selecionados))
        ]

        # Agrupar por região
        df_regiao = df_regiao.groupby("Regiao")["Valor_m2"].mean().reset_index()

        st.dataframe(df_regiao)

        fig_regiao = px.bar(
            df_regiao,
            x="Regiao",
            y="Valor_m2",
            color="Valor_m2",
            text="Valor_m2",
            color_continuous_scale="Viridis",
            labels={"Valor_m2":"Valor médio m²","Regiao":"Região"},
            title=f"Comparação de Custo Médio por m² entre Regiões Selecionadas ({', '.join(meses_selecionados)})"
        )
        fig_regiao.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_regiao, use_container_width=True)
    else:
        st.warning("Selecione ao menos uma região e um mês para visualizar o gráfico.")

else:
    st.warning("Nenhum dado disponível para os filtros selecionados.")