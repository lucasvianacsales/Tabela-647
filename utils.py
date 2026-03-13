import streamlit as st
import pandas as pd

def filtros_laterais(df):
    """Cria filtros padrão na lateral e retorna os valores selecionados e o df filtrado"""
    
    st.sidebar.header("Filtros")
    
    ufs = ["Todos"] + sorted(df["UF"].unique())
    uf_selecionada = st.sidebar.selectbox("Selecione o UF:", options=ufs)
    
    meses = ["Todos"] + sorted(df["Mes"].unique())
    mes_selecionado = st.sidebar.selectbox("Selecione o Mês:", options=meses)
    
    anos = ["Todos"] + sorted(df["Ano"].unique())
    ano_selecionado = st.sidebar.selectbox("Selecione o Ano:", options=anos)
    
    padrao_selecionados = st.sidebar.multiselect(
        "Selecione Padrão(s) de Acabamento:",
        options=sorted(df["Padrao_Acabamento"].unique()),
        default=df["Padrao_Acabamento"].unique()
    )
    
    tipos_selecionados = st.sidebar.multiselect(
        "Selecione Tipo(s) de Projeto:",
        options=sorted(df["Tipo_Projeto"].unique()),
        default=df["Tipo_Projeto"].unique()
    )
    
    # Filtrar dados
    df_filtrado = df[
        (df["Tipo_Projeto"].isin(tipos_selecionados)) &
        (df["Padrao_Acabamento"].isin(padrao_selecionados))
    ]
    
    if uf_selecionada != "Todos":
        df_filtrado = df_filtrado[df_filtrado["UF"] == uf_selecionada]
    
    if mes_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Mes"] == mes_selecionado]
    
    if ano_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Ano"] == ano_selecionado]
    
    return df_filtrado