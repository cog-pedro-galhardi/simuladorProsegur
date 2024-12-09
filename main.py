import streamlit as st
import pandas as pd
from absenteismo import calculate_absenteism
from simulador import monte_carlo_simulation, simulation_results, prepare_data

# Configurações de layout
st.set_page_config(page_title="Simulador", page_icon="assets/cog.png")
st.markdown(
    """
    <style>

    div.stButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    div.stDownloadButton > button {
        background-color: #007BFF;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: none;
        font-size: 16px;
    }

    div.stDownloadButton > button:hover {
        background-color: #0056b3;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<h1 style='color: #007BFF;'>Simulador</h1>", unsafe_allow_html=True)

# sidebar para o menu de navegação
st.sidebar.title("Menu de Navegação")
menu_option = st.sidebar.radio(
    "Navegue para:",
    [
        "Previsão de Demanda",
        "Modelo de Otimização",
        "Modelo de Simulação",
    ],
)

if menu_option == "Previsão de Demanda":
    st.sidebar.write("Redirecionando para Previsão de Demanda ")
    st.sidebar.markdown(
        "[Clique aqui](https://prossegurprevisao-cognitivo.streamlit.app/)",
        unsafe_allow_html=True,
    )

elif menu_option == "Modelo de Otimização":
    st.sidebar.write("Redirecionando para Modelo de Otimização")
    st.sidebar.markdown(
        "[Clique aqui](http://54.211.109.72:8501/)", unsafe_allow_html=True
    )

elif menu_option == "Modelo de Simulação":
    st.sidebar.write("Redirecionando para Modelo de Simulação")
    st.sidebar.markdown(
        "[Clique aqui](http://54.211.109.72:8502/)",
        unsafe_allow_html=True,
    )


def load_file(file, enconding=None):
    if enconding:
        return pd.read_csv(file, sep=";", encoding=enconding)
    else:
        return pd.read_csv(file, sep=";")


# output paths
absentesimo_result_filepath = "./outputs/absenteismo.csv"
simulation_result_filepath = "./outputs/simulacoes.csv"
results_1_filepath = "./outputs/df1.csv"
results_2_filepath = "./outputs/df2.csv"
results_3_filepath = "./outputs/df3.csv"
results_4_filepath = "./outputs/df4.csv"


# Carregar os dados
st.markdown(
    "<h5 style='color: #007BFF;'>Selecione o arquivo de absenteísmo</h5>",
    unsafe_allow_html=True,
)
abs_filepath = st.file_uploader("Carregar: ", type="csv", key="abs_file_uploader")


# Absenteismo
if st.button("Calcular Taxa Absenteísmo"):
    if abs_filepath is not None:
        try:
            # Carregar dados
            input_abs_df = load_file(abs_filepath, "latin1")

            # Calcula o absenteismo
            abs_df = calculate_absenteism(input_abs_df)
            st.write("Taxa de Absenteísmo (5 primeiras linhas): ")
            st.write(abs_df.head())

            st.session_state["abs"] = abs_df

            abs_df.to_csv(absentesimo_result_filepath, index=False)

        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    else:
        st.error("Por favor, carregue o arquivo TXT necessário.")

# Simulacoes

if "abs" in st.session_state:
    st.markdown(
        "<h5 style='color: #007BFF;'>Selecione o arquivo de previsão de demanda</h5>",
        unsafe_allow_html=True,
    )
    demand_filepath = st.file_uploader(
        "Carregar: ", type="csv", key="demand_file_uploader"
    )

    st.markdown(
        "<h5 style='color: #007BFF;'>Selecione o arquivo de escala</h5>",
        unsafe_allow_html=True,
    )
    escala_filepath = st.file_uploader(
        "Carregar: ", type="csv", key="escala_file_uploader"
    )

    if demand_filepath is not None and escala_filepath is not None:
        st.markdown(
            "<h2 style='color: #007BFF;'>Parâmetros para simulação</h2>",
            unsafe_allow_html=True,
        )
        n_simulacoes = st.number_input(
            "Quantidade de simulações", min_value=1, max_value=10000, value=1000
        )

        if st.button("Processar Simulações"):
            try:
                # Carregar dados
                input_demand_df = load_file(demand_filepath)
                input_escala_df = load_file(escala_filepath)
                abs_df = st.session_state["abs"]
                # Tratamento dos dados
                escala_df = prepare_data(input_demand_df, input_escala_df, abs_df)
                # Executar simulação
                simulation_df = monte_carlo_simulation(
                    escala_df, input_demand_df, n_simulacoes
                )
                # Visualização
                df1, df2, df3, df4 = simulation_results(simulation_df)

                # Calcula o absenteismo
                st.write("Simulações (5 primeiras linhas): ")
                st.write(simulation_df.head())

                st.session_state["sim"] = simulation_df
                st.session_state["df1"] = df1
                st.session_state["df2"] = df2
                st.session_state["df3"] = df3
                st.session_state["df4"] = df4

                simulation_df.to_csv(simulation_result_filepath, index=False)
                df1.to_csv(results_1_filepath, index=False)
                df2.to_csv(results_2_filepath, index=False)
                df3.to_csv(results_3_filepath, index=False)
                df4.to_csv(results_4_filepath, index=False)

            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
        else:
            st.error("Por favor, carregue os arquivos CSV necessários.")

# Resultados
if "abs" in st.session_state and "sim" in st.session_state:
    # Carregar dados
    df1 = st.session_state["df1"]
    df2 = st.session_state["df2"]
    df3 = st.session_state["df3"]
    df4 = st.session_state["df4"]
    # Mostrar dados
    st.markdown(
        "<h5 style='color: #007BFF;'>Resultados:</h5>",
        unsafe_allow_html=True,
    )
    st.write("Visão Filial, Cargo, Mês, Faixa: ")
    st.write(df1)
    st.write("Visão Filial, Cargo, Mês: ")
    st.write(df2)
    st.write("Visão Filial, Cargo: ")
    st.write(df3)
    st.write("Visão Filial: ")
    st.write(df4)
