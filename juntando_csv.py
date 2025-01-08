import os
from pyspark.sql import SparkSession

# Verificando o diretório de trabalho
print("Diretório atual:", os.getcwd())

# Inicializa a sessão do Spark
spark = SparkSession.builder.appName("UniaoCSV").getOrCreate()

# Lê os arquivos CSV no diretório relativo
df_combined = spark.read.csv("file:///C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/bruto/*.csv", header=True, inferSchema=True)


# Exibe as 5 primeiras linhas do DataFrame
df_combined

num_rows = df_combined.count()
print(f"O DataFrame possui {num_rows} registros.")
df_combined.coalesce(1).write.option("header", "true").csv("file:///C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/saida_combined")

# Finaliza a sessão do Spark
spark.stop()
