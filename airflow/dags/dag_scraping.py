from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Garante que o Airflow ache o scrapping.py na raiz montada
sys.path.append("/opt/airflow")

from scrapping import run_scraping

# Argumentos padrão da DAG
default_args = {
    "owner": "nicolas",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

# Define a DAG para rodar todo dia 1 às 3 da manhã
with DAG(
    dag_id="scraping_farfetch_mensal",
    default_args=default_args,
    description="Executa o scraping da Farfetch uma vez por mês",
    schedule_interval="0 10 1 * *",  # todo dia 1 do mês às 10:00
    start_date=datetime(2024, 4, 1),
    catchup=False,             
    max_active_runs=1,
    tags=["scraping", "selenium", "mensal"],
) as dag:

    tarefa_scraping = PythonOperator(
        task_id="executar_scraping_farfetch",
        python_callable=run_scraping
    )

    tarefa_scraping
