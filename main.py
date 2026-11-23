import math
import pandas as pd
from association import bulk_pair_binary_stats
from conf_lift_table import build_consequence_table, append_averages
from conf_lift_support import format_conf_lift_support

# 1. Carregar TabelaDengue.csv mantendo os 'X' originais (exigido pelo association.py)
df = pd.read_csv('TabelaDengue.csv', sep=';', encoding='latin1')
df.columns = df.columns.str.strip()
# Remove colunas vazias 'Unnamed' geradas pelo Excel
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Remove linhas fantasmas sem PEID, caso existam
if 'PEID' in df.columns:
    df = df.dropna(subset=['PEID'])

total_n = len(df)
consequence_cols = ['ConfirmedDengue']
premise_cols = [c for c in df.columns if c not in ['PEID', 'ConfirmedDengue']]

# 2. Estágio 1: Calcular estatísticas e montar tabela de tuplas (conf, lift, support)
resultados = bulk_pair_binary_stats(df, premise_cols, consequence_cols, total_n)
tabela_bruta = build_consequence_table(resultados, premise_cols, consequence_cols, is_a_to_b=True)

# 3. Filtragem de Suporte >= 0.10 (10%) e Confiança >= 0.10 (10%) ANTES da formatação em texto
suporte_min = 0.10
confianca_min = 0.10

atributos_filtrados = []
linhas_numericas = []

for atributo in tabela_bruta.index:
    conf, lift, sup = tabela_bruta.loc[atributo, 'ConfirmedDengue']
    if sup >= suporte_min and conf >= confianca_min:
        atributos_filtrados.append(atributo)
        linhas_numericas.append({
            'Atributo': atributo,
            'Confianca': conf,
            'Lift': lift,
            'Suporte': sup
        })

tabela_filtrada = tabela_bruta.loc[atributos_filtrados]

# 4. Estágios 2 e 3: Adicionar médias/DP e formatar como "conf (lift) [support]"
tabela_com_medias = append_averages(tabela_filtrada, axis=0)
tabela_formatada = format_conf_lift_support(tabela_com_medias, decimals=2)

# 5. Exportar os dois arquivos CSV
tabela_formatada.to_csv('Matriz_Dengue_Lift_Formatado.csv', sep=';', encoding='latin1')

df_numerico = pd.DataFrame(linhas_numericas).sort_values(by='Lift', ascending=False)
df_numerico.to_csv('Matriz_Dengue_Lift_Numerico.csv', sep=';', index=False, encoding='latin1', decimal=',')

print("Arquivos gerados com sucesso!")