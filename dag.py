# dag_farfetch_scraper.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from scrapping import run_scraping  # Função de scraping

default_args = {
    'owner': 'nicolas',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

#Define start date um dia antes para executar o codigo agora
start_date = datetime.now() - timedelta(days=1)

with DAG(
    'farfetch_scraper_dag',
    default_args=default_args,
    description='DAG para scraping de produtos da Farfetch, executada mensalmente',
    schedule_interval="@monthly",  # Rodar mensalmente
    start_date=start_date,
    catchup=False,
) as dag:

    run_scraping_task = PythonOperator(
        task_id='run_scraping',
        python_callable=run_scraping,
    )

    run_scraping_task