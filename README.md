# Cálculo de Suporte, Confiança e Lift para Tabelas Binárias

Este repositório contém um conjunto de scripts em Python para calcular métricas de Regras de Associação (**Suporte**, **Confiança** e **Lift**) a partir de planilhas binárias em formato `.csv` (como tabelas preparadas para Análise Formal de Conceitos / Lattice Miner).

---

## Resumo dos Arquivos

* **`association.py`**: Motor matemático do projeto. Lê as colunas marcadas com `'X'`, conta as ocorrências e calcula Suporte, Confiança (nos dois sentidos) e Lift par a par.
* **`conf_lift_table.py`**: Organiza os resultados em uma tabela estruturada de tuplas `(confiança, lift, suporte)`, adiciona as linhas de **Média** e **Desvio Padrão (DP)** e trunca os valores decimais.
* **`conf_lift_support.py`**: Formata cada célula da tabela no padrão compacto **`conf (lift) [support]`** (ex: `0.80 (1.76) [0.18]`), pronto para relatórios e artigos.
* **`main.py`**: Script principal que você deve executar. Carrega a planilha `.csv`, limpa colunas vazias do Excel, aplica os filtros de Suporte e Confiança mínimos e exporta os resultados finais.

---

## Requisitos e Formato da Planilha

1. **Bibliotecas Python** (requer `pandas` versão 2.1 ou superior):
   ```bash
   pip install pandas numpy
   ```
2. **Formato do `.csv` de entrada**:
   * **Base completa obrigatória:** A tabela deve conter **todos os registros juntos** (casos positivos e negativos na mesma planilha). Sem os casos negativos, o cálculo do Lift perde o contraste e fica travado em $1.00$.
   * **Marcação binária:** Presenças devem estar marcadas com **`X`** (ou `x`) e ausências devem ficar **vazias**.
   * **Separador padrão:** Ponto e vírgula (`;`) e codificação `latin1` (padrão do Excel em português).

---

## Quais Linhas Alterar para Usar na Sua Base (`main.py`)

Para adaptar o código a outro projeto, você só precisa editar o arquivo **`main.py`** nas seguintes linhas:

| Linha(s) em `main.py` | Código Atual | O que alterar |
| :---: | :--- | :--- |
| **Linha 8** | `pd.read_csv('TabelaDengue.csv', sep=';', encoding='latin1')` | Troque `'TabelaDengue.csv'` pelo nome do seu arquivo. Se o separador for vírgula, mude `sep=','`. |
| **Linhas 14–15** | `if 'PEID' in df.columns:`<br>`df = df.dropna(subset=['PEID'])` | Troque `'PEID'` pelo nome da coluna de identificação (ID) da sua tabela (ou apague essas duas linhas se não tiver ID). |
| **Linha 18** | `consequence_cols = ['ConfirmedDengue']` | Troque `'ConfirmedDengue'` pelo nome exato da sua **coluna alvo** (consequência). |
| **Linha 19** | `premise_cols = [c for c in df.columns if c not in ['PEID', 'ConfirmedDengue']]` | Atualize `'PEID'` e `'ConfirmedDengue'` com os nomes das colunas que **não** devem entrar como premissas. |
| **Linhas 26–27** | `suporte_min = 0.10`<br>`confianca_min = 0.10` | Ajuste os filtros mínimos desejados (ex: `0.05` para $5\%$, ou `0.0` para não filtrar nada). |
| **Linha 33** | `tabela_bruta.loc[atributo, 'ConfirmedDengue']` | **Importante:** Troque `'ConfirmedDengue'` aqui também pelo nome da sua nova coluna alvo. |
| **Linhas 50 e 53** | `'Matriz_Dengue_Lift_Formatado.csv'`<br>`'Matriz_Dengue_Lift_Numerico.csv'` | Altere os nomes dos arquivos `.csv` de saída como preferir. |

> **Dica (`association.py`, linhas 5–6):** Se a sua planilha usa `1` e `0` em vez de `X` e vazio, basta trocar `== 'X'` por `== '1'` nas linhas 5 e 6 do arquivo `association.py`.

---

## Como Executar

Coloque os 4 arquivos `.py` e a sua planilha `.csv` na **mesma pasta**, abra o terminal nessa pasta e rode:

```bash
python main.py
```

### Arquivos Gerados

* **`NomeEscolhido_Formatado.csv`**: Tabela formatada como `Confiança (Lift) [Suporte]` com Média e Desvio Padrão no rodapé.
* **`NomeEscolhido_Lift_Numerico.csv`**: Tabela com colunas numéricas separadas, ordenada do maior para o menor **Lift** (ideal para ordenar e gerar gráficos no Excel).

### Leitura Rápida do Lift

$$\text{Lift}(A, B) = \frac{P(A \cap B)}{P(A) \times P(B)}$$

* **$\text{Lift} > 1.00$**: Associação positiva (o atributo aumenta a chance do alvo).
* **$\text{Lift} \approx 1.00$**: Independência / neutro (o atributo aparece na mesma proporção nos dois grupos).
* **$\text{Lift} < 1.00$**: Associação negativa (o atributo diminui a chance do alvo).