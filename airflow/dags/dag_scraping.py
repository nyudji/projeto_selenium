import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


# Adiciona a pasta /opt/airflow/scrapping ao sys.path
sys.path.insert(0, '/opt/airflow/scrapping')

# Importação dentro da função para evitar erros de carregamento do DAG
def run_scraping_task():
    from scrapping import run_scraping  # Importação do módulo 'scrapping'
    run_scraping()

# Definição do DAG
with DAG(
    dag_id='scraping_dag',
    description='Um DAG para rodar o scraping',
    schedule_interval='@daily',  # Corrigido para `schedule_interval`
    start_date=datetime(2025, 3, 24),
    catchup=False,
    tags=['scraping'],  # Adicionado uma tag para facilitar organização no Airflow UI
) as dag:

    # Criando a tarefa PythonOperator para rodar o scraping
    run_scraping_operator = PythonOperator(
        task_id='run_scraping',
        python_callable=run_scraping_task,  # Chama a função que executa o scraping
    )
