import streamlit as st
import pandas as pd
from utils import filtros_laterais  # função de filtros reutilizável

st.title("Visualização do Dataset")

# -----------------------------
# CARREGAR DATASET
# -----------------------------
df = pd.read_csv("dataset.csv")
df.columns = df.columns.str.strip()

# Normaliza a coluna Mes para abreviação
df["Mes_Abr"] = df["Mes"].str.strip().str[:3].str.capitalize()

# -----------------------------
# APLICAR FILTROS
# -----------------------------
df_filtrado = filtros_laterais(df)

# -----------------------------
# ORDENAR DATASET
# -----------------------------
df_filtrado = df_filtrado.sort_values(by=["UF", "Mes_Abr"], ascending=[True, True])

# -----------------------------
# REMOVER COLUNA AUXILIAR
# -----------------------------
df_filtrado = df_filtrado.drop(columns=["Mes_Abr"], errors="ignore")

# -----------------------------
# FORMATAR VALOR_M2 COM DUAS CASAS DECIMAIS
# -----------------------------
df_filtrado["Valor_m2"] = df_filtrado["Valor_m2"].map(lambda x: f"{x:.2f}")

# -----------------------------
# COLOCAR DESCRICAO NO FINAL
# -----------------------------
cols = [c for c in df_filtrado.columns if c != "Descricao"] + ["Descricao"]
df_filtrado = df_filtrado[cols]

# -----------------------------
# EXIBIR DATASET
# -----------------------------
st.subheader("Dataset Filtrado")
st.dataframe(df_filtrado)

# -----------------------------
# MÉTRICAS
# -----------------------------
st.subheader("Métricas")
col1, col2, col3 = st.columns(3)

if not df_filtrado.empty:
    valor_float = df_filtrado["Valor_m2"].astype(float)
    col1.metric("Valor mínimo por m²", round(valor_float.min(), 2))
    col2.metric("Valor médio por m²", round(valor_float.mean(), 2))
    col3.metric("Valor máximo por m²", round(valor_float.max(), 2))
else:
    col1.metric("Valor mínimo por m²", 0)
    col2.metric("Valor médio por m²", 0)
    col3.metric("Valor máximo por m²", 0)