import streamlit as st
import pandas as pd
import pickle

st.set_page_config(page_title="Previsão de Custo por m²", layout="wide")
st.title("Previsão de Custo por m²")

# -----------------------------
# CARREGAR DADOS
# -----------------------------
@st.cache_data
def carregar_dataset():
    df = pd.read_csv("dataset.csv")
    df.columns = df.columns.str.strip()

    df["UF"] = df["UF"].astype(str).str.strip()
    df["Padrao_Acabamento"] = df["Padrao_Acabamento"].astype(str).str.strip()
    df["Mes"] = df["Mes"].astype(str).str.strip().str.capitalize()
    df["Tipo_Projeto"] = df["Tipo_Projeto"].astype(str).str.strip()
    df["Ano"] = pd.to_numeric(df["Ano"], errors="coerce")
    df["Valor_m2"] = pd.to_numeric(df["Valor_m2"], errors="coerce")

    return df

@st.cache_resource
def carregar_modelo():
    with open("modelo.pkl", "rb") as f:
        return pickle.load(f)

df = carregar_dataset()
modelo = carregar_modelo()

# -----------------------------
# LISTAS PARA OS CAMPOS
# -----------------------------
meses_ordem = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

ufs = sorted(df["UF"].dropna().unique())
padroes = sorted(df["Padrao_Acabamento"].dropna().unique())
tipos = sorted(df["Tipo_Projeto"].dropna().unique())
meses_presentes = [m for m in meses_ordem if m in df["Mes"].dropna().unique()]

# apenas anos futuros para previsão
anos_previsao = list(range(2026, 2031))
indice_padrao_ano = 0

# -----------------------------
# CAMPOS DE ENTRADA
# -----------------------------
col1, col2 = st.columns(2)

uf = col1.selectbox("Estado", ufs)
padrao = col1.selectbox("Padrão de Acabamento", padroes)

mes = col2.selectbox("Mês", meses_presentes)
ano = col2.selectbox("Ano da previsão", anos_previsao, index=indice_padrao_ano)

tipo = st.selectbox("Tipo de Projeto", tipos)

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
    # REFERÊNCIA HISTÓRICA
    # mesmo UF + Mês + Padrão + Tipo
    # -----------------------------
    filtro_ref = df[
        (df["UF"] == uf) &
        (df["Mes"] == mes) &
        (df["Padrao_Acabamento"] == padrao) &
        (df["Tipo_Projeto"] == tipo)
    ].copy()

    if not filtro_ref.empty:
        ultimo_ano = int(filtro_ref["Ano"].max())
        valor_ultimo = filtro_ref.loc[filtro_ref["Ano"] == ultimo_ano, "Valor_m2"].mean()

        minimo_historico = filtro_ref["Valor_m2"].min()
        maximo_historico = filtro_ref["Valor_m2"].max()

        diferenca_percentual = ((previsao - valor_ultimo) / valor_ultimo) * 100

        limite_superior = valor_ultimo * 1.10
        limite_inferior = valor_ultimo * 0.90

        st.write("### Referência histórica")
        st.write(f"**Último valor observado ({ultimo_ano}):** R$ {valor_ultimo:.2f}/m²")
        st.write(f"**Menor valor histórico:** R$ {minimo_historico:.2f}/m²")
        st.write(f"**Maior valor histórico:** R$ {maximo_historico:.2f}/m²")

        if previsao > limite_superior:
            st.warning(
                f"🚨 O custo previsto para {ano} está {abs(diferenca_percentual):.1f}% acima "
                f"do último valor observado para {uf} / {mes} / {padrao} / {tipo}."
            )
        elif previsao < limite_inferior:
            st.info(
                f"✅ O custo previsto para {ano} está {abs(diferenca_percentual):.1f}% abaixo "
                f"do último valor observado para {uf} / {mes} / {padrao} / {tipo}."
            )
        else:
            st.success(
                f"✔️ O custo previsto para {ano} está próximo do último valor observado para esse cenário."
            )

        with st.expander("Ver base histórica usada no alerta"):
            st.dataframe(
                filtro_ref[["UF", "Mes", "Ano", "Padrao_Acabamento", "Tipo_Projeto", "Valor_m2"]]
                .sort_values(["Ano", "Mes"]),
                use_container_width=True
            )
    else:
        st.caption("Não foi encontrada base histórica de comparação para esse cenário.")