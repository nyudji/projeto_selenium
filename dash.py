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
        dados_tratatos = 'dados/tratado/jaquetas_tratado.csv'
        # Ler o arquivo csv
        st.write("Dados Tratados")
        data2 = pd.read_csv(dados_tratatos)
        st.dataframe(data2)  # Exibe os dados como tabela
        # Adicione gráficos e outras análises a partir do DataFrame `data`
    else:
        st.warning("Nenhum arquivo de dados encontrado. Execute o scraping para preencher o dashboard.")

