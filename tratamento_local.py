from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, regexp_replace, round, when, ltrim, trim, lit
import os
import glob
from pyspark.sql.utils import AnalysisException
from datetime import datetime
import shutil
import pyspark
import time
from dash import get_latest_file 
from db.create_table import create_table
from db.insert_db import insert_postgres
from db.create_db import create_database
from db.config import DB_CONFIG

def tratamento(): 
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

        #Adiciona a data e hora do scraping 
        df_jaquetas = df_jaquetas.withColumn("Data", lit(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))

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
            output_path_csv = "file:///C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/csv"
            output_path_parquet = "file:///C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/parquet"
            df_jaquetas.coalesce(1).write.csv(output_path_csv, mode="append", header=True)
            try:
                df_existing = spark.read.parquet(output_path_parquet)
                # Combine com os dados de df_jaquetas
                df_combined = df_existing.union(df_jaquetas)
            except Exception:
                # Se o diretório estiver vazio ou não existir, use apenas df_jaquetas
                df_combined = df_jaquetas

            # Consolidar em um único arquivo e sobrescrever
            df_combined.coalesce(1).write.mode("append").parquet(output_path_parquet)

            # Caminho de saída para os arquivos tratados
            output_path2 = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/csv"
            output_path1 = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado/parquet"
            
            print('Tratamento salvo em dado/tratado')
            for file in os.listdir(output_path2):
                if file.startswith("part-") and file.endswith(".csv"):
                    full_path = os.path.join(output_path2, file)
                    #Valida que o arquivo não está vazio
                    if os.path.getsize(full_path) > 0:
                        shutil.copy(full_path, os.path.join(output_path2, "jaquetas_tratado.csv"))
                        print("Arquivo CSV renomeado com sucesso!")
                        #Tempo de espera em segundos (exemplo: 30 segundos)
                        tempo_espera = 15

                        #Espera para permitir a validação
                        print(f"Aguardando {tempo_espera} segundos para validar o processo...")
                        time.sleep(tempo_espera)

                        #Remove arquivos desnecessários (_SUCCESS e .crc)
                        for file in os.listdir(output_path2):
                            if file.startswith("_SUCCESS") or file.endswith(".crc") or file.startswith("part-"):
                                os.remove(os.path.join(output_path2, file))

                        print("Arquivos auxiliares removidos após o tempo de espera.")


            for file in os.listdir(output_path1):
                if file.startswith("part-") and file.endswith(".parquet"):
                    full_path = os.path.join(output_path1, file)
                    
                    #Valida que o arquivo não está vazio
                    if os.path.getsize(full_path) > 0:
                        shutil.copy(full_path, os.path.join(output_path1, "dados_tratado.parquet"))
                        print("Arquivo parquet copiado renomeado com sucesso!")
                        
                        #Tempo de espera em segundos (exemplo: 30 segundos)
                        tempo_espera = 15

                        #Espera para permitir a validação
                        print(f"Aguardando {tempo_espera} segundos para validar o processo...")
                        time.sleep(tempo_espera)

                        #Remove arquivos desnecessários (_SUCCESS e .crc)
                        for file in os.listdir(output_path1):
                            if file.startswith("_SUCCESS") or file.endswith(".crc") or file.startswith("part-"):
                                os.remove(os.path.join(output_path1, file))

                        print("Arquivos auxiliares removidos após o tempo de espera.")
            df_pandas = df_jaquetas.select("Produto", "Preço", "Preço Original", "Desconto", "Desconto Percentual", "Categoria Luxo", 'Classificação',"Data").toPandas()
            df_pandas.to_csv('C:\\Users\\JPA\\Desktop\\Projetos\\Selenium\\projeto_selenium\\dados\\tratado\\csv\\jaquetas_todos.csv', mode='a', header=True, index=False)
            print("Arquivo CSV com todos criado com sucesso!") 
            # Criar o banco, se não existir
            create_database(DB_CONFIG['database'])
            create_table()
            
            insert_postgres(df_pandas)
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")
        #Encerrando a sessão do Spark
        spark.stop()
        print('Spark parado')
            
    except AnalysisException as e:
        print(f"Erro ao processar o arquivo CSV: {e}")
        input("Pressione Enter para continuar...")