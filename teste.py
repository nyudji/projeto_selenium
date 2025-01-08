import pandas as pd
file_path = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/parquet/dados_tratado.parquet"
df = pd.read_parquet(file_path)
df.head(500)
