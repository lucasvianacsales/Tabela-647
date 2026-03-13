import streamlit as st
import pandas as pd
import pickle

st.title("Previsão de Custo por m²")

# Carregar dataset
df = pd.read_csv(r"C:\Analista de Dados\case\dataset.csv")
df.columns = df.columns.str.strip()

# Normaliza os meses para comparar
df["Mes_clean"] = df["Mes"].str.strip().str.capitalize()

with open(r"C:\Analista de Dados\case\modelo.pkl", "rb") as f:
    modelo = pickle.load(f)

col1, col2 = st.columns(2)

uf = col1.selectbox(
    "Estado",
    sorted(df["UF"].unique())
)

padrao = col1.selectbox(
    "Padrão de Acabamento",
    sorted(df["Padrao_Acabamento"].unique())
)

# Ordem completa dos meses
meses_ordem = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
               "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]

# Pega os meses que existem no dataset, mantendo ordem do calendário
meses_presentes = [m for m in meses_ordem if m in df["Mes_clean"].unique()]

mes = col2.selectbox(
    "Mês",
    meses_presentes
)

tipo = col2.selectbox(
    "Tipo de Projeto",
    sorted(df["Tipo_Projeto"].unique())
)

if st.button("Calcular custo estimado"):

    # Converter de volta para o formato original do CSV, se necessário
    entrada = pd.DataFrame({
        "UF":[uf],
        "Padrao_Acabamento":[padrao],
        "Mes":[mes],
        "Tipo_Projeto":[tipo]
    })

    previsao = modelo.predict(entrada)[0]

    st.success(f"Custo estimado: R$ {previsao:.2f} por m²")