import streamlit as st
import pandas as pd
import glob
import os


def get_latest_file(pattern="promocoes_jaquetas_*.csv"):
    # Obter o caminho absoluto para o diretório 'dados/bruto' relativo ao diretório atual
    pasta_base = os.path.join(os.getcwd(), 'dados', 'bruto')  # Garante que o caminho é montado a partir da raiz do projeto

    # Garantir que a pasta existe
    if not os.path.exists(pasta_base):
        print(f"Pasta não encontrada: {pasta_base}")
        return None

    # Construir o caminho completo com o padrão
    caminho_completo = os.path.join(pasta_base, pattern)

    # Procurar por todos os arquivos que correspondem ao padrão
    arquivos = glob.glob(caminho_completo)
    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return None  # Retorna None se não houver arquivos correspondentes

    # Selecionar o arquivo com a data mais recente no nome
    arquivo_mais_recente = max(arquivos, key=os.path.getctime)
    return arquivo_mais_recente



def display_dashboard():
    arquivo_mais_recente = get_latest_file()
    print(arquivo_mais_recente)
    if arquivo_mais_recente:
        data = pd.read_csv(arquivo_mais_recente)
        st.dataframe(data)  # Exibe os dados como tabela
        dados_tratatos = 'dados/tratado/csv/jaquetas_tratado.csv'
        # Ler o arquivo csv
        st.write("Dados Tratados")
        data2 = pd.read_csv(dados_tratatos)
        st.dataframe(data2)  # Exibe os dados como tabela
        # Adicione gráficos e outras análises a partir do DataFrame `data`
    else:
        st.warning("Nenhum arquivo de dados encontrado. Execute o scraping para preencher o dashboard.")

def display_dash2():
    # Pegando dados 
    @st.cache_data
    def get_data():
        df_todos = pd.read_parquet('./dados/tratado/parquet/dados_tratado.parquet')
        return df_todos

    df = get_data()

    # Sidebar para filtros
    st.sidebar.header('Faça o filtro aqui')

    # Filtro: Classificação
    classificacao = st.sidebar.multiselect(
        "Classificação",
        options=df['Classificação'].unique(),
        default=df['Classificação'].unique()
    )

    # Filtro: Categoria
    categorias = st.sidebar.selectbox(
        "Categoria",
        options=["Todos"] + list(df['Categoria Luxo'].unique())
    )

    # Filtro: Desconto
    desconto = st.sidebar.slider(
        "Desconto (em %)",
        min_value=0,
        max_value=100,
        value=(0, 100)  # Range inicial: 0 a 100%
    )

    # Aplicação dos filtros
    df_filtrado = df.copy()
    if classificacao:
        df_filtrado = df_filtrado[df_filtrado['Classificação'].isin(classificacao)]

    if categorias != "Todos":
        df_filtrado = df_filtrado[df_filtrado['Categoria Luxo'] == categorias]

    df_filtrado = df_filtrado[
        (df_filtrado['Desconto Percentual'] >= desconto[0]) & 
        (df_filtrado['Desconto Percentual'] <= desconto[1])
    ]

    #Calculando KPI's
    preco_medio = int(df_filtrado['Preço'].mean())
    desconto_medio = int(df_filtrado['Desconto Percentual'].mean())
    contagem_produtos = df_filtrado.shape[0]

    col1, col2, col3, = st.columns(3)
    with col1:
        st.subheader('Preço médio')
        st.subheader(f'R$: {preco_medio:,}')
    with col2:
        st.subheader('Desconto médio')
        st.subheader(f'{desconto_medio:,}%')
    with col3:
        st.subheader('Total ofertas')
        st.subheader(f'{contagem_produtos}')

    # Exibição do DataFrame filtrado
    st.dataframe(df_filtrado, use_container_width=True)
