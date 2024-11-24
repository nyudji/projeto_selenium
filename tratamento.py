from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, regexp_replace, round, when, ltrim, trim
import os
import glob
from pyspark.sql.utils import AnalysisException
from datetime import datetime
import shutil
import pyspark
import time
from dash import get_latest_file 

#Le o arquivo
try:
    arquivo_mais_recente = get_latest_file()
    print(f"Arquivo mais recente encontrado: {arquivo_mais_recente}")
except FileNotFoundError as e:
    print(e)
    input("Pressione Enter para continuar...") 

#Inicia/Cria a SparkSession
spark = SparkSession.builder \
    .appName("Calcula desconto")\
    .getOrCreate()
#Continua o problema ate onde der
spark.sparkContext.setLogLevel("ERROR")
print (arquivo_mais_recente)
try:
    #Lendo o CSV com caminho absoluto local (com prefixo file:///)
    df_jaquetas = spark.read.csv("file:///" + arquivo_mais_recente.replace("\\", "/"), header=True, inferSchema=True)

    #Remover espaços à esquerda (antes do nome do produto)
    df_jaquetas = df_jaquetas.withColumn("Produto", trim(col("Produto")))

    #Limpeza e transformação dos preços
    df_jaquetas = df_jaquetas.withColumn(
        "Preço", 
        regexp_replace(col("Preço"), "R\\$|\\.", "").cast("float")
    )

    df_jaquetas = df_jaquetas.withColumn(
        "Preço Original", 
        regexp_replace(col("Preço Original"), "R\\$|\\.", "").cast("float")
    )

    #Calculando o desconto
    df_jaquetas = df_jaquetas.withColumn(
        "Desconto", round((col("Preço Original") - col("Preço")) / col("Preço Original"), 4)
    )

    #Removendo o .0 do preço final, convertendo para inteiro
    df_jaquetas = df_jaquetas.withColumn(
        "Preço", col("Preço").cast("int")
    )
    df_jaquetas = df_jaquetas.withColumn(
        "Preço Original", col("Preço Original").cast("int")
    )
    df_jaquetas = df_jaquetas.withColumn(
        "Preço", col("Preço Original").cast("int")
    )
    #Categorizando Luxo
    df_jaquetas = df_jaquetas.withColumn(
        "Categoria Luxo",
        when(col("Preço") < 2000, "Pouco Luxoso")
        .when((col("Preço") >= 2000) & (col("Preço") < 10000), "Luxoso")
        .otherwise("Muito Luxuoso")
    )

    #Verificando se o produto tem valor maior ou menor que a media
    media_preco = df_jaquetas.agg({"Preço": "avg"}).collect()[0][0]
    df_jaquetas = df_jaquetas.withColumn(
        "Media",
        when(col("Preço") > media_preco, "Alta")
        .otherwise("Baixa")
    )

    print('Preço medio dos produtos', media_preco)

    #Criando uma coluna de desconto percentual
    df_jaquetas = df_jaquetas.withColumn(
        "Desconto Percentual", round(col("Desconto") * 100, 2)
    )


    #Classificação
    df_jaquetas = df_jaquetas.withColumn(
        "Classificação",
        when(col("Produto").rlike("Jaqueta"), "Jaqueta")
        .when(col("Produto").rlike("Blazer"), "Blazer")
        .when(col("Produto").rlike("Camisa"), "Camisa")
        .when(col("Produto").rlike("Colete"), "Colete")
        .otherwise("Diferentes")

    )

    #Mostrando o resultado
    df_jaquetas.show()
    
    #Tente salvar o DataFrame diretamente no caminho local
    try:
    
        #Criando um DataFrame de exemplo
        data = [("João", 30), ("Maria", 25), ("Pedro", 35)]
        columns = ["Nome", "Idade"]

        df = spark.createDataFrame(data, columns)
                # Forçando o DataFrame a ser escrito em um único arquivo
        output_path = "file:///C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado"
        df_jaquetas.coalesce(1).write.csv(output_path, mode="overwrite", header=True)
        output_path2 = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado"
        #Encerrando a sessão do Spark
        spark.stop()
        print('Spark parado')
        print('Tratamento salvo em dado/tratado')

        for file in os.listdir(output_path2):
            if file.startswith("part-") and file.endswith(".csv"):
                full_path = os.path.join(output_path2, file)
                
                #Valida que o arquivo não está vazio
                if os.path.getsize(full_path) > 0:
                    os.rename(full_path, os.path.join(output_path2, "jaquetas_tratado.csv"))
                    print("Arquivo renomeado com sucesso!")
                    
                    #Tempo de espera em segundos (exemplo: 30 segundos)
                    tempo_espera = 120

                    #Espera para permitir a validação
                    print(f"Aguardando {tempo_espera} segundos para validar o processo...")
                    time.sleep(tempo_espera)

                    #Remove arquivos desnecessários (_SUCCESS e .crc)
                    for file in os.listdir(output_path2):
                        if file.startswith("_SUCCESS") or file.endswith(".crc"):
                            os.remove(os.path.join(output_path2, file))

                    print("Arquivos auxiliares removidos após o tempo de espera.")
            
    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")
        
except AnalysisException as e:
    print(f"Erro ao processar o arquivo CSV: {e}")
    input("Pressione Enter para continuar...")