import streamlit as st
import pandas as pd
import glob
import os
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.colors as pc

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

    # Filtro: Categoria
    marcas = st.sidebar.selectbox(
        "Marca",
        options=["Todas"] + list(df['Marca'].unique())
    )

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
    
    if marcas != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Marca'] == marcas]

    df_filtrado = df_filtrado[
        (df_filtrado['Desconto Percentual'] >= desconto[0]) & 
        (df_filtrado['Desconto Percentual'] <= desconto[1])
    ]

    

    #Calculando KPI's
    preco_medio = int(df_filtrado['Preço'].mean())
    desconto_medio = int(df_filtrado['Desconto Percentual'].mean())
    contagem_produtos = df_filtrado.shape[0]
    st.divider()
    col1, col2, col3, = st.columns(3)
    with col1:
        st.subheader('Preço médio')
        st.subheader(f'R$ {preco_medio:,}')
    with col2:
        st.subheader('Desconto médio')
        st.subheader(f'{desconto_medio:,}%')
    with col3:
        st.subheader('Total ofertas')
        st.subheader(f'{contagem_produtos}')
    st.divider()


    def plot_top10_descontos(df):
        """Cria um gráfico de barras dos produtos com maior desconto, com fundo transparente."""
        fig, ax = plt.subplots(figsize=(8, 5))

        # Criar o gráfico de barras
        sns.barplot(
            data=df, 
            y="Produto", 
            x="Desconto Real", 
            ax=ax, 
            palette="Reds_r"
        )

        # Configurar fundo transparente
        fig.patch.set_alpha(0)  # Fundo da figura transparente
        ax.set_facecolor("none")  # Fundo do gráfico transparente

        # Ajustar rótulos e título
        ax.set_xlabel("Desconto em R$", color="white")
        ax.set_ylabel("Produto", color="white")
        ax.set_title("Produtos com maiores descontos", color="white")

        # Ajustar cores dos ticks (valores nos eixos)
        ax.tick_params(colors="white")

        return fig
    
    #Botao mostrar tabela
     # Estado inicial para exibição da tabela
    if 'show_table' not in st.session_state:
        st.session_state.show_table = False

    # Botão para alternar a exibição
    if st.button("Exibir/Ocultar Tabela"):
        st.session_state.show_table = not st.session_state.show_table

    def plot_tipo_desconto(df):
        """Cria um gráfico de boxplot com fundo transparente."""
        fig, ax = plt.subplots(figsize=(8, 5))

        # Criar o boxplot
        sns.boxplot(
            data=df, 
            x="Classificação", 
            y="Desconto Percentual", 
            ax=ax, 
            palette="coolwarm"
        )

        # Configurar fundo transparente
        fig.patch.set_alpha(0)  # Fundo da figura transparente
        ax.set_facecolor("none")  # Fundo do gráfico transparente

        # Ajustar cores dos rótulos e título
        ax.set_xlabel("Tipo", color="white")
        ax.set_ylabel("Desconto (%)", color="white")
        ax.set_title("Descontos (%) por Tipo do produto", color="white", fontsize=25)

        # Ajustar cores dos ticks (valores nos eixos)
        ax.tick_params(colors="white")

        return fig
    
    # Exibir a tabela se o estado for True
    if st.session_state.show_table:
        st.dataframe(df_filtrado, use_container_width=True)
    
    # Adicionar um divisor abaixo
    st.divider()


    #Mostrar produtos com maiores descontos
    # Calcular o desconto real
    df_filtrado["Desconto Real"] = df_filtrado["Preço Original"] - df_filtrado["Preço"]
    top10_descontos = df_filtrado.nlargest(50, "Desconto Real")

    #Exibe os produtos com maiores desconto
    st.pyplot(plot_top10_descontos(top10_descontos))
    st.divider()

    # Criar colunas para exibir os gráficos lado a lado
    col4, col5 = st.columns(2)

    # Grafico esquerda , produtos por categoria
    with col4:
        fig_prod_cat = px.pie(df_filtrado, names="Categoria Luxo", title="Produtos por Categoria", hole=0.4, color_discrete_sequence=pc.qualitative.Pastel1)
        st.plotly_chart(fig_prod_cat)
    # Gráfico da direita, Tipo x Desconto
    with col5:
        st.pyplot(plot_tipo_desconto(df_filtrado))
    
    # Ordenar o DataFrame com base na contagem de ofertas por marca
    df_ordenado = df_filtrado.groupby("Marca").size().reset_index(name="Contagem").sort_values(by="Contagem", ascending=False)
    
    # Criar o gráfico de barras com uma sequência de cores personalizada
    fig_contagem_marca = px.bar(
        df_ordenado,
        x="Marca",
        y="Contagem",
        title="Contagem de Ofertas Por Marcas",
        color_discrete_sequence=["#F4CED9"] * len(df_ordenado)  # Cor personalizada
    )

    fig_preco_marca = df_filtrado.groupby(by=["Marca"])[["Preço"]].sum().sort_values(by="Preço")

    fig_preco_marca = px.bar(
        fig_preco_marca,
        x="Preço",
        y=fig_preco_marca.index,
        orientation="h",
        title="<b>Preços Total por Marca</b>",
        color_discrete_sequence=["#F4CED9"] * len(fig_preco_marca),
        template="plotly_white",
    )

    fig_preco_marca.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )
    
    if marcas == "Todas":
        left_column, right_column = st.columns(2)
        left_column.plotly_chart(fig_contagem_marca, use_container_width=True)
        right_column.plotly_chart(fig_preco_marca, use_container_width=True)
        
        fig_dist_preco = px.box(
        df_filtrado,
        x="Marca",
        y="Preço",
        color="Marca",
        title="Distribuição de Preços por Marca",
        color_discrete_sequence=px.colors.sequential.Plasma  # Paleta de degradê
        )
        st.plotly_chart(fig_dist_preco, use_container_width=True)

    
    st.divider()


    