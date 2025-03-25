# Usa uma imagem base do Python 3.8
FROM python:3.8-slim

# Atualizar pip antes de instalar as dependências
RUN pip install --upgrade pip

RUN apt-get update && apt-get install -y supervisor



# Copiar o arquivo requirements.txt para o contêiner (verifique o caminho correto)
COPY requirements.txt /opt/airflow/requirements.txt

# Instalar dependências do sistema necessárias (se necessário)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Definindo o diretório de trabalho
WORKDIR /opt/airflow

# Instalando o Airflow com suporte para Celery Executor
RUN pip install apache-airflow[celery]==2.6.3

# Copiando o diretório dags para dentro do container
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins

# Instalar as dependências do requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Definindo variáveis de ambiente
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
ENV AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
ENV AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@postgres/airflow
ENV AIRFLOW__WEBSERVER__SECRET_KEY=mysecretkey

# Expondo a porta do Airflow
EXPOSE 8080

# Definindo o comando de inicialização
CMD ["airflow", "webserver"]

# Copia o código-fonte da aplicação para dentro do contêiner
COPY . .

# Copiar o restante dos arquivos do projeto para dentro do contêiner
COPY ./dags /opt/airflow/dags
COPY ./plugins /opt/airflow/plugins
