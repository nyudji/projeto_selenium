@echo off
echo Iniciando o Airflow...
docker-compose up -d

echo Criando usuário Admin...
docker-compose run airflow-worker airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin