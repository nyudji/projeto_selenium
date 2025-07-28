from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, regexp_replace, round, when, ltrim, trim, lit
import os
import glob
from pyspark.sql.utils import AnalysisException
from datetime import datetime
import shutil
import pyspark
import time
from app.dash import get_latest_file 
from db.create_table import create_table
from db.insert_db import insert_postgres
from db.create_db import create_database
from db.config import DB_CONFIG

def tratamento(): 
    try:
        arquivo_mais_recente = get_latest_file()
        print(f"Arquivo mais recente encontrado: {arquivo_mais_recente}")
    except FileNotFoundError as e:
        print(e)
        input("Pressione Enter para continuar...") 

    spark = SparkSession.builder \
        .appName("Calcula desconto")\
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    print(arquivo_mais_recente)

    try:
        df_jaquetas = spark.read.csv("file:///" + arquivo_mais_recente.replace("\\", "/"), header=True, inferSchema=True)
        df_jaquetas = df_jaquetas.withColumn("Data", lit(datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
        df_jaquetas = df_jaquetas.withColumn("Produto", trim(col("Produto")))

        df_jaquetas = df_jaquetas.withColumn("Preço", regexp_replace(col("Preço"), "R\\$|\\.", "").cast("float"))
        df_jaquetas = df_jaquetas.withColumn("Preço Original", regexp_replace(col("Preço Original"), "R\\$|\\.", "").cast("float"))

        df_jaquetas = df_jaquetas.withColumn("Desconto", round((col("Preço Original") - col("Preço")) / col("Preço Original"), 4))

        df_jaquetas = df_jaquetas.withColumn("Preço", col("Preço").cast("int"))
        df_jaquetas = df_jaquetas.withColumn("Preço Original", col("Preço Original").cast("int"))

        df_jaquetas = df_jaquetas.withColumn("Categoria Luxo", when(col("Preço") < 2000, "Pouco Luxoso")
            .when((col("Preço") >= 2000) & (col("Preço") < 10000), "Luxoso")
            .otherwise("Muito Luxuoso"))

        media_preco = df_jaquetas.agg({"Preço": "avg"}).collect()[0][0]
        df_jaquetas = df_jaquetas.withColumn("Media", when(col("Preço") > media_preco, "Alta").otherwise("Baixa"))

        print('Preço medio dos produtos', media_preco)

        df_jaquetas = df_jaquetas.withColumn("Desconto Percentual", round(col("Desconto") * 100, 2))

        df_jaquetas = df_jaquetas.withColumn("Classificação",
            when(col("Produto").rlike("Jaqueta"), "Jaqueta")
            .when(col("Produto").rlike("Blazer"), "Blazer")
            .when(col("Produto").rlike("Camisa"), "Camisa")
            .when(col("Produto").rlike("Colete"), "Colete")
            .otherwise("Diferentes"))

        df_jaquetas.show()

        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        output_path_csv = f"file:///{os.path.join(base_dir, 'dados', 'tratado', 'csv').replace(os.sep, '/')}"
        output_path_parquet = f"file:///{os.path.join(base_dir, 'dados', 'tratado', 'parquet').replace(os.sep, '/')}"

        output_path_csv_fs = os.path.join(base_dir, 'dados', 'tratado', 'csv')
        output_path_parquet_fs = os.path.join(base_dir, 'dados', 'tratado', 'parquet')

        os.makedirs(output_path_csv_fs, exist_ok=True)
        os.makedirs(output_path_parquet_fs, exist_ok=True)

        df_jaquetas.coalesce(1).write.csv(output_path_csv, mode="append", header=True)
        try:
            df_existing = spark.read.parquet(output_path_parquet)
            df_combined = df_existing.union(df_jaquetas)
        except Exception:
            df_combined = df_jaquetas

        df_combined.coalesce(1).write.mode("append").parquet(output_path_parquet)

        print('Tratamento salvo em dado/tratado')
        for file in os.listdir(output_path_csv_fs):
            if file.startswith("part-") and file.endswith(".csv"):
                full_path = os.path.join(output_path_csv_fs, file)
                if os.path.getsize(full_path) > 0:
                    shutil.copy(full_path, os.path.join(output_path_csv_fs, "jaquetas_tratado.csv"))
                    print("Arquivo CSV renomeado com sucesso!")
                    time.sleep(15)
                    for file in os.listdir(output_path_csv_fs):
                        if file.startswith("_SUCCESS") or file.endswith(".crc") or file.startswith("part-"):
                            os.remove(os.path.join(output_path_csv_fs, file))
                    print("Arquivos auxiliares removidos após o tempo de espera.")

        for file in os.listdir(output_path_parquet_fs):
            if file.startswith("part-") and file.endswith(".parquet"):
                full_path = os.path.join(output_path_parquet_fs, file)
                if os.path.getsize(full_path) > 0:
                    shutil.copy(full_path, os.path.join(output_path_parquet_fs, "dados_tratado.parquet"))
                    print("Arquivo parquet copiado renomeado com sucesso!")
                    time.sleep(15)
                    for file in os.listdir(output_path_parquet_fs):
                        if file.startswith("_SUCCESS") or file.endswith(".crc") or file.startswith("part-"):
                            os.remove(os.path.join(output_path_parquet_fs, file))
                    print("Arquivos auxiliares removidos após o tempo de espera.")

        df_pandas = df_jaquetas.select("Produto", "Preço", "Preço Original", "Desconto", "Desconto Percentual", "Categoria Luxo", 'Classificação',"Data").toPandas()
        df_pandas.to_csv(os.path.join(output_path_csv_fs, "jaquetas_todos.csv"), mode='a', header=True, index=False)
        print("Arquivo CSV com todos criado com sucesso!") 

        create_database(DB_CONFIG['database'])
        create_table()
        insert_postgres(df_pandas)

    except Exception as e:
        print(f"Erro ao salvar o arquivo: {e}")

    spark.stop()
    print('Spark parado')
