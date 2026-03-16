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

# anos para previsão futura
anos_previsao = list(range(2021, 2031))
indice_padrao_ano = anos_previsao.index(2026) if 2026 in anos_previsao else 0

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
    # usando somente os anos históricos do dataset
    # -----------------------------
    filtro_ref = df[
        (df["UF"] == uf) &
        (df["Mes"] == mes) &
        (df["Padrao_Acabamento"] == padrao) &
        (df["Tipo_Projeto"] == tipo)
    ].copy()

    if not filtro_ref.empty:
        media_referencia = filtro_ref["Valor_m2"].mean()
        minimo_historico = filtro_ref["Valor_m2"].min()
        maximo_historico = filtro_ref["Valor_m2"].max()
        diferenca_percentual = ((previsao - media_referencia) / media_referencia) * 100

        limite_superior = media_referencia * 1.10
        limite_inferior = media_referencia * 0.90

        ano_min = int(filtro_ref["Ano"].min())
        ano_max = int(filtro_ref["Ano"].max())

        st.write("### Referência histórica")
        st.write(f"**Média histórica ({ano_min}–{ano_max}):** R$ {media_referencia:.2f}/m²")
        st.write(f"**Menor valor observado:** R$ {minimo_historico:.2f}/m²")
        st.write(f"**Maior valor observado:** R$ {maximo_historico:.2f}/m²")

        if previsao > limite_superior:
            st.warning(
                f"🚨 O custo previsto para {ano} está {abs(diferenca_percentual):.1f}% acima "
                f"da média histórica para {uf} / {mes} / {padrao} / {tipo}."
            )
        elif previsao < limite_inferior:
            st.info(
                f"✅ O custo previsto para {ano} está {abs(diferenca_percentual):.1f}% abaixo "
                f"da média histórica para {uf} / {mes} / {padrao} / {tipo}."
            )
        else:
            st.success(
                f"✔️ O custo previsto para {ano} está dentro da faixa esperada para esse cenário."
            )

        with st.expander("Ver base histórica usada no alerta"):
            st.dataframe(
                filtro_ref[["UF", "Mes", "Ano", "Padrao_Acabamento", "Tipo_Projeto", "Valor_m2"]]
                .sort_values(["Ano", "Mes"]),
                use_container_width=True
            )
    else:
        st.caption("Não foi encontrada base histórica de comparação para esse cenário.")