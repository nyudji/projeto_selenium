#!/bin/bash
set -e

# Adiciona o mapeamento de localhost para o IP do serviço 'app_db'
# 'app_db' é o nome do serviço PostgreSQL do seu app no docker-compose.yml
# O comando 'getent hosts app_db' resolve o nome do serviço para seu IP interno
echo "$(getent hosts app_db | awk '{ print $1 }') localhost" >> /etc/hosts

# Executa o comando original do contêiner (o comando Airflow)
exec "$@"