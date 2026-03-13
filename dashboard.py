import streamlit as st

st.set_page_config(
    page_title="Dashboard - Custo de Projetos m²",
    layout="wide"
)

st.title("Dashboard de Custos de Projetos")

st.write("""
Bem-vindo ao dashboard de análise de custos por m².

Este sistema permite:

• Analisar custos históricos de projetos  
• Visualizar gráficos e métricas  
• Filtrar dados por estado, mês e tipo de projeto  
• Estimar custos utilizando Machine Learning
""")

st.divider()

st.subheader("Navegação")

st.write("""
Utilize o menu lateral para acessar:

**Dataset** → visualizar os dados filtrados  
**Análise Gráfica** → gráficos e métricas  
**Previsão** → estimativa de custo por m²
""")