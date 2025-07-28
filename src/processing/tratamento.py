from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, round, when, trim, lit
from pyspark.sql.utils import AnalysisException
import os
import shutil
import time
import glob
import logging
from datetime import datetime
from db.create_table import create_table
from db.insert_db import insert_postgres
from db.create_db import create_database
from db.config import DB_CONFIG

# Configura o logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_latest_file(pattern="promocoes_jaquetas_*.csv"):
    """
    Retorna o caminho do arquivo CSV mais recente na pasta /opt/airflow/dados/bruto
    """
    pasta_base = "/opt/airflow/dados/bruto"

    if not os.path.exists(pasta_base):
        raise FileNotFoundError(f"Pasta não encontrada: {pasta_base}")

    caminho_completo = os.path.join(pasta_base, pattern)
    arquivos = glob.glob(caminho_completo)

    if not arquivos:
        raise FileNotFoundError(f"Nenhum arquivo com padrão '{pattern}' encontrado em {pasta_base}")

    return max(arquivos, key=os.path.getmtime)

def tratamento():
    try:
        arquivo_mais_recente = get_latest_file()
        logging.info(f"Arquivo mais recente encontrado: {arquivo_mais_recente}")
    except FileNotFoundError as e:
        logging.error(f"Erro ao localizar arquivo: {e}")
        return

    spark = SparkSession.builder.appName("Tratamento Ofertas").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    try:
        df_jaquetas = spark.read.csv("file:///" + arquivo_mais_recente.replace("\\", "/"), header=True, inferSchema=True)
        # Adiciona a data e hora do scraping
        data_scraping = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        df_jaquetas = df_jaquetas.withColumn("Data", lit(data_scraping))
        df_jaquetas = df_jaquetas.withColumn("Produto", trim(col("Produto")))
        df_jaquetas = df_jaquetas.withColumn("Preço", regexp_replace(col("Preço"), "R\\$|\\.", "").cast("float"))
        df_jaquetas = df_jaquetas.withColumn("Preço Original", regexp_replace(col("Preço Original"), "R\\$|\\.", "").cast("float"))
        df_jaquetas = df_jaquetas.withColumn("Desconto", round((col("Preço Original") - col("Preço")) / col("Preço Original"), 4))
        df_jaquetas = df_jaquetas.withColumn("Preço", col("Preço").cast("int"))
        df_jaquetas = df_jaquetas.withColumn("Preço Original", col("Preço Original").cast("int"))

        df_jaquetas = df_jaquetas.withColumn(
            "Categoria Luxo",
            when(col("Preço") < 2000, "Pouco Luxoso")
            .when((col("Preço") >= 2000) & (col("Preço") < 10000), "Luxoso")
            .otherwise("Muito Luxuoso")
        )

        media_preco = df_jaquetas.agg({"Preço": "avg"}).collect()[0][0]
        df_jaquetas = df_jaquetas.withColumn(
            "Media",
            when(col("Preço") > media_preco, "Alta").otherwise("Baixa")
        )

        df_jaquetas = df_jaquetas.withColumn("Desconto Percentual", round(col("Desconto") * 100, 2))

        df_jaquetas = df_jaquetas.withColumn(
            "Classificação",
            when(col("Produto").rlike("Jaqueta"), "Jaqueta")
            .when(col("Produto").rlike("Blazer"), "Blazer")
            .when(col("Produto").rlike("Camisa"), "Camisa")
            .when(col("Produto").rlike("Colete"), "Colete")
            .otherwise("Diferentes")
        )

        df_jaquetas.show()

        # Diretórios de saída
        path_base = "/opt/airflow/dados/tratado"
        path_csv = os.path.join(path_base, "csv")
        path_parquet = os.path.join(path_base, "parquet")
        output_path_parquet = f"file:///{os.path.join('/opt/airflow', 'dados', 'tratado', 'parquet').replace(os.sep, '/')}"
        logging.info(output_path_parquet)
        logging.info(path_parquet)
        os.makedirs(path_csv, exist_ok=True)
        os.makedirs(path_parquet, exist_ok=True)

        # Salvar CSV
        df_jaquetas.coalesce(1).write.csv(f"file://{path_csv}", mode="append", header=True)
        for file in os.listdir(path_csv):
            if file.startswith("part-") and file.endswith(".csv"):
                full_path = os.path.join(path_csv, file)
                if os.path.getsize(full_path) > 0:
                    shutil.move(full_path, os.path.join(path_csv, "jaquetas_tratado.csv"))
                    logging.info("CSV tratado salvo como jaquetas_tratado.csv")
                    time.sleep(5)
                    for lixo in os.listdir(path_csv):
                        if lixo.startswith("_SUCCESS") or lixo.endswith(".crc") or lixo.startswith("part-"):
                            os.remove(os.path.join(path_csv, lixo))

        # Salvar Parquet
        try:
            # Se o diretório Parquet já existe e contém arquivos
            if os.path.exists(path_parquet) and os.listdir(path_parquet):
                logging.info(f"Lendo Parquet existente de: {path_parquet}")
                df_existente = spark.read.parquet(output_path_parquet)
                logging.info("Lido")
                df_completo = df_existente.union(df_jaquetas) # Union by name para compatibilidade de schema
            else:
                # Se o diretório está vazio ou não existe, apenas escreva o novo DataFrame
                logging.info(f"Criando novo Parquet em: {path_parquet}")
                df_completo = df_jaquetas
        except Exception as e:
            logging.error(f"Erro ao salvar Parquet: {e}")
        
        # Sobrescrever o diretório Parquet com o DataFrame combinado.
        # Isso apaga o conteúdo antigo do diretório e escreve os novos 'part-' files.
        df_completo.coalesce(1).write.mode("append").parquet(output_path_parquet)
        logging.info(f"Parquet criado em {output_path_parquet}")

        # Remover apenas os arquivos de controle do Spark (_SUCCESS, .crc),
        for file in os.listdir(path_parquet):
            if file.startswith("part-") and file.endswith(".parquet"):
                full_path = os.path.join(path_parquet, file)
                if os.path.getsize(full_path) > 0:
                    shutil.copy(full_path, os.path.join(path_parquet, "dados_tratado.parquet"))
                    print("Arquivo parquet copiado e renomeado com sucesso!")
                    time.sleep(15)
                    for lixo in os.listdir(path_parquet):
                        if lixo.startswith("_SUCCESS") or lixo.endswith(".crc") or lixo.startswith("part-"):
                            os.remove(os.path.join(path_parquet, lixo))
                    print("Arquivos auxiliares removidos após o tempo de espera.")
        logging.info("Arquivos auxiliares Parquet (se houver) removidos.")

        # Exportar também para CSV geral com Pandas
        df_jaquetas.toPandas().to_csv(os.path.join(path_csv, "jaquetas_todos.csv"), mode='a', header=True, index=False)
        logging.info("CSV consolidado (jaquetas_todos.csv) salvo com sucesso.")

        #Transforma tabela em pandas
        df_pandas = df_jaquetas.select("Produto", "Preço", "Preço Original", "Desconto", "Desconto Percentual", "Categoria Luxo", 'Classificação',"Data").toPandas()

        # Criar o banco, se não existir
        create_database(DB_CONFIG['database'])
        create_table()
        insert_postgres(df_pandas)

        spark.stop()
        logging.info("Spark encerrado com sucesso.")

    except AnalysisException as e:
        logging.error(f"Erro no processamento do CSV: {e}")
        spark.stop()