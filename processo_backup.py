import pandas as pd
import os
import sys
import time
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

# -----------------------------
# CABEÇALHO
# -----------------------------
print("="*60)
print("PROCESSANDO TABELA 647 - CUSTO DE PROJETO m²")
print("="*60)

# -----------------------------
# DEFINIR ARQUIVO
# -----------------------------
if len(sys.argv) > 1:
    arquivo = sys.argv[1]
else:
    arquivo = r"C:\Users\Mônica Gabriela\Tabela-647\tabela.csv"

if not os.path.exists(arquivo):
    sys.exit("ERRO: Arquivo não encontrado.")

pasta_saida = r"C:\Users\Mônica Gabriela\Tabela-647"
if not os.path.exists(pasta_saida):
    os.makedirs(pasta_saida)

dataset_saida = os.path.join(pasta_saida, "dataset.csv")
modelo_saida = os.path.join(pasta_saida, "modelo.pkl")

print(f"Arquivo recebido: {arquivo}")
print(f"Dataset salvo em: {dataset_saida}\n\n")

# -----------------------------
# CONFIGURAÇÕES
# -----------------------------
tipos_projeto = ['CP.1-2Q', 'CR.1-3Q', 'PR4-3QP', 'PC.12-LA', 'CB-MMO']
descricoes = [
    'Casa popular (1 pav, varanda, sala, 2 quartos)',
    'Casa residencial (1 pav, 3 quartos)',
    'Prédio residencial (4 pavimentos)',
    'Prédio comercial (12 pavimentos)',
    'Cesta básica construção'
]

# -----------------------------
# LER ARQUIVO
# -----------------------------
try:
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
except:
    with open(arquivo, 'r', encoding='latin-1') as f:
        linhas = f.readlines()

# -----------------------------
# IDENTIFICAR MESES
# -----------------------------
meses_raw = linhas[3].split(',')[3:]
meses = []

for mes in meses_raw:
    mes_clean = mes.replace('"', '').strip()
    if mes_clean and mes_clean not in meses:
        meses.append(mes_clean)

# -----------------------------
# PROCESSAR DADOS
# -----------------------------
dados_longos = []

for linha_num in range(5, len(linhas)):
    linha = linhas[linha_num].strip()
    if not linha or linha.startswith('"Fonte') or linha.startswith('"Notas'):
        continue

    campos = linha.split(',')
    if len(campos) < 4:
        continue

    codigo = campos[0].replace('"', '')
    uf = campos[1].replace('"', '').strip()
    padrao = campos[2].replace('"', '')
    valores = campos[3:]

    for pos, valor in enumerate(valores):
        valor_clean = valor.replace('"', '').strip()
        if valor_clean in ['-', '']:
            continue
        try:
            valor_float = float(valor_clean)
            mes_idx = pos // 5
            tipo_idx = pos % 5
            if mes_idx < len(meses):
                mes_full = meses[mes_idx].strip()
                partes = mes_full.split()
                mes_nome = partes[0]
                ano = partes[1] if len(partes) > 1 else ""
                dados_longos.append({
                    'Codigo_IBGE': codigo,
                    'UF': uf,
                    'Padrao_Acabamento': padrao,
                    'Mes': mes_nome,
                    'Ano': ano,
                    'Tipo_Projeto': tipos_projeto[tipo_idx],
                    'Descricao': descricoes[tipo_idx],
                    'Valor_m2': valor_float
                })
        except:
            continue

# -----------------------------
# CRIAR DATAFRAME
# -----------------------------
df = pd.DataFrame(dados_longos)

# -----------------------------
# MAPEAR REGIÕES
# -----------------------------
nordeste = ["Ceará","Bahia","Pernambuco","Rio Grande do Norte","Paraíba",
            "Piauí","Maranhão","Alagoas","Sergipe"]
sudeste = ["São Paulo","Rio de Janeiro","Minas Gerais","Espírito Santo"]
sul = ["Paraná","Santa Catarina","Rio Grande do Sul"]
centro_oeste = ["Distrito Federal","Goiás","Mato Grosso","Mato Grosso do Sul"]
norte = ["Acre","Amapá","Amazonas","Roraima","Pará","Tocantins","Rondônia"]

def mapear_regiao(estado):
    estado_norm = estado.strip().lower()
    if estado_norm in [e.lower() for e in nordeste]:
        return "Nordeste"
    elif estado_norm in [e.lower() for e in sudeste]:
        return "Sudeste"
    elif estado_norm in [e.lower() for e in sul]:
        return "Sul"
    elif estado_norm in [e.lower() for e in centro_oeste]:
        return "Centro-Oeste"
    elif estado_norm in [e.lower() for e in norte]:
        return "Norte"
    else:
        return "Desconhecida"

df["Regiao"] = df["UF"].apply(mapear_regiao)

# -----------------------------
# SALVAR DATASET
# -----------------------------
df.to_csv(dataset_saida, index=False, encoding='utf-8-sig')

# -----------------------------
# TREINAR MODELO
# -----------------------------
print("Treinando modelo de Machine Learning...\n\n")

X = df[["UF", "Padrao_Acabamento", "Mes", "Tipo_Projeto"]]
y = df["Valor_m2"]

colunas_categoricas = ["UF", "Padrao_Acabamento", "Mes", "Tipo_Projeto"]

preprocessador = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), colunas_categoricas)]
)

modelo = RandomForestRegressor(n_estimators=50, random_state=42)
pipeline = Pipeline([("preprocessamento", preprocessador), ("modelo", modelo)])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
pipeline.fit(X_train, y_train)

previsoes = pipeline.predict(X_test)

# -----------------------------
# AVALIAR MODELO
# -----------------------------
score = r2_score(y_test, previsoes)
print(f"Precisão do modelo (R²): {round(score,3)}")
with open(modelo_saida, "wb") as f:
    pickle.dump(pipeline, f)
print(f"Modelo salvo em: {modelo_saida}")
print("="*60)
print("PROCESSAMENTO FINALIZADO")
print("="*60)

time.sleep(5)