import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def prepare_data(demand_df, escala_df, abs_df):
    demand_df['data'] = pd.to_datetime(demand_df['data'], format='%d/%m/%Y')
    escala_df['data'] = pd.to_datetime(escala_df['data'], format='%d/%m/%Y')
    # Merge da escala com o absenteísmo e filtrar colaboradores escalados
    # escala_trabalhando = input_escala_df.merge(abs_df[['cod_filial', 'nome', 'tx_absenteismo']],
    # on=['cod_filial', 'nome'], how='left')
    escala_trabalhando = escala_df.merge(abs_df[['nome', 'tx_absenteismo']], on=['nome'], how='left')
    escala_trabalhando = escala_trabalhando[
        (escala_trabalhando['marcacao'] == 'E') & (escala_trabalhando['data'].isin(demand_df['data']))
        ]
    return escala_trabalhando


def monte_carlo_simulation(escala_df, demanda_df, n_simulacoes=1000):
    """
    Executa a simulação de Monte Carlo para o absenteísmo.

    Args:
        escala_df (pd.DataFrame): DataFrame de escala já filtrado.
        demanda_df (pd.DataFrame): DataFrame de demanda.
        n_simulacoes (int): Número de simulações.

    Returns:
        pd.DataFrame: DataFrame consolidado com resultados das simulações.
    """
    # Definir as colunas-chave para agrupamento
    chave_cols = ['data', 'cod_filial', 'cargo']
    demanda_cols = ['data', 'cod_filial', 'cargo', 'faixa', 'quantidade']

    # Preparar a base de demanda
    demanda_base = demanda_df[demanda_cols].copy()

    # Preparar a base de escala: cada colaborador por data/cod_filial/cargo
    escala_base = escala_df[['data', 'cod_filial', 'cargo', 'nome', 'tx_absenteismo']].copy()

    # Expandir escala_base para todas as simulações
    escala_expanded = escala_base.loc[np.repeat(escala_base.index.values, n_simulacoes)].reset_index(drop=True)
    escala_expanded['simulacao'] = np.tile(np.arange(n_simulacoes), len(escala_base))

    # Simular presença para cada colaborador e cada simulação
    random_vals = np.random.rand(len(escala_expanded))
    escala_expanded['presente'] = random_vals > escala_expanded['tx_absenteismo']

    # Calcular número de presentes por simulação, data, cod_filial e cargo
    presenca = escala_expanded[escala_expanded['presente']].groupby(['simulacao'] + chave_cols).size().reset_index(name='n_presentes')

    # Expandir demanda_base para todas as simulações
    demanda_expanded = demanda_base.loc[np.repeat(demanda_base.index.values, n_simulacoes)].reset_index(drop=True)
    demanda_expanded['simulacao'] = np.tile(np.arange(n_simulacoes), len(demanda_base))

    # Realizar o merge entre demanda_expanded e presenca
    demanda_simulada = demanda_expanded.merge(presenca, on=chave_cols + ['simulacao'], how='left')
    demanda_simulada['n_presentes'] = demanda_simulada['n_presentes'].fillna(0).astype(int)

    # Calcular demanda não atendida
    demanda_simulada['demanda_nao_atendida'] = np.maximum(demanda_simulada['quantidade'] - demanda_simulada['n_presentes'], 0)

    return demanda_simulada


# Função para plotar estatísticas
def plot_estatisticas(estatisticas, filial, cargo, faixa):
    """
    Plota as estatísticas da demanda não atendida para uma filial e cargo específicos.

    Args:
        estatisticas (pd.DataFrame): DataFrame com estatísticas.
        filial (int): Código da filial.
        cargo (str): Nome do cargo.
        faixa (str): Faixa de hora.
    """
    dados = estatisticas[(estatisticas['cod_filial'] == filial) & (estatisticas['cargo'] == cargo) & (estatisticas['faixa'] == faixa)].sort_values('data')

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.plot(dados['data'], dados['mean'], label='Média', marker='o')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('Demanda Não Atendida')
    ax1.tick_params(axis='x', rotation=45)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    ax2.plot(dados['data'], dados['std'], label='Desvio Padrão', color='purple', linestyle='--', marker='x')
    ax2.set_ylabel('Desvio Padrão')
    ax2.legend(loc='upper right')

    plt.title(f'Estatísticas da Demanda Não Atendida\nFilial: {filial}, Cargo: {cargo}')
    plt.tight_layout()
    plt.show()


def simulation_results(resultados_df):

    # Adicionar a coluna 'mês' ao DataFrame
    resultados_df['mês'] = resultados_df['data'].dt.to_period('M')

    # DataFrame 1: mês, data, cod_filial, cargo, faixa, demanda, Média demanda_nao_atendida
    df1 = resultados_df.groupby(['mês', 'data', 'cod_filial', 'cargo', 'faixa']).agg({
        'quantidade': 'first', 'demanda_nao_atendida': 'mean'}).reset_index()

    # Renomear as colunas conforme necessário
    df1.rename(columns={'demanda_nao_atendida': 'faltaEsperada'}, inplace=True)

    # DataFrame 2: mês, data, cod_filial, cargo, soma demanda por faixa, soma da Média demanda_nao_atendida
    df2 = df1.groupby(['mês', 'data', 'cod_filial', 'cargo']).agg({
        'quantidade': 'sum', 'faltaEsperada': 'sum'}).reset_index()

    # DataFrame 3: cod_filial, 'cargo', média da soma demanda por cargo e faixa,
    # média da soma da Média demanda_nao_atendida, soma da soma da Média demanda_nao_atendida
    df3 = df2.groupby(['cod_filial', 'cargo']).agg({
        'quantidade': 'mean', 'faltaEsperada': ['mean', 'sum']}).reset_index()

    # Ajustar os nomes das colunas
    df3.columns = ['cod_filial', 'cargo', 'quantidade', 'media_faltaEsperada', 'soma_faltaEsperada']

    # DataFrame 4: cod_filial, média da soma demanda por cargo e faixa,
    # média da soma da Média demanda_nao_atendida, soma da soma da Média demanda_nao_atendida
    df4 = df3.groupby(['cod_filial']).agg({
        'quantidade': 'mean', 'media_faltaEsperada': ['mean'], 'soma_faltaEsperada': ['sum']
    }).reset_index()

    # Ajustar os nomes das colunas
    df4.columns = ['cod_filial', 'quantidade', 'media_faltaEsperada', 'soma_faltaEsperada']

    return df1, df2, df3, df4
