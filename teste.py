import pandas as pd
file_path = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/parquet/part-00000-00d98b38-0668-494e-87ba-cbd47775bb1e-c000.snappy.parquet"
df = pd.read_parquet(file_path)
df.head(100)