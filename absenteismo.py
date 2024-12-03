import pandas as pd

# Lista das colunas que indicam faltas
falta_columns = [
    'FALTAINTEGRAL',
    'DOENCATRABAL',
    'DOENCA',
    'SERVMILITAR',
    'LICENCPATERN',
    'AFASTEMPRE',
    'ATESTMEDICOINT',
    'FALECIMENTO',
    'AFASTAMENTO',
    'ABONOGREVE',
    'DISPJUSTICA',
    'DISPONUSEMPRESA',
    'AFASTSINDICANCIA',
    'ATESTMEDICACIDTRABA',
    'DISPFENONATUREZA',
    'ABONOACOMPANHAMENTO',
    'FENONATUREZA',
    'ATESTMEDICOPARC',
    'ATESTMEDICOS19',
    'ATESTMEDICOC19',
    'ABONOCOVID19'
]


# Função para verificar se houve falta em um dia
def is_falta(row):
    return any(row[col] != '0:00' for col in falta_columns)


def calculate_absenteism(df):

    # Converter a coluna de data para datetime
    df['DFOCODATA'] = pd.to_datetime(df['DFOCODATA'], format='%d/%m/%Y')

    # Criar uma coluna 'mes' para facilitar a agregação mensal
    df['mes'] = df['DFOCODATA'].dt.to_period('M')

    # Padronizar os nomes para facilitar o merge posterior
    df['nome'] = df['NOME'].str.strip().str.upper()

    # Aplicar a função para criar uma coluna 'falta' (1 se houve falta, 0 caso contrário)
    df['falta'] = df.apply(is_falta, axis=1).astype(int)

    # Agrupar por NOME e mês para contar o total de faltas
    df_abs = df.groupby(['nome', 'mes'])['falta'].sum().reset_index()

    # Calcular a taxa de absenteísmo (n_faltas / 21)
    df_abs['tx_absenteismo'] = df_abs['falta'] / 21

    return df_abs
