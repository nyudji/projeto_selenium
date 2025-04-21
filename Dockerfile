#Utiliza o airflow 2.10.5
FROM apache/airflow:2.10.5

# Atualizar pip antes de instalar as dependências
RUN pip install --upgrade pip setuptools wheel

# Instalando cython
RUN pip install --no-cache-dir Cython

# Copiar o arquivo requirements.txt para o contêiner (verifique o caminho correto)
COPY ./requirements.txt /opt/airflow/requirements.txt

# Definindo usuario root
USER root

# Cria pasta de logs do airflow
RUN mkdir -p /opt/airflow/logs && chmod -R 755 /opt/airflow/logs

#Cria pasta de logs do scheduler do airflow
RUN mkdir -p /opt/airflow/logs/scheduler && chmod -R 755 /opt/airflow/logs/scheduler

# Instalar dependências do sistema necessárias (se necessário)
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    libpq-dev \
    zlib1g-dev \
    libyaml-dev \
    python3-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    firefox-esr \
    xvfb \
    build-essential \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/* \
    && chmod -R 755 /var/lib/apt/lists

# Instalar o Java 11 (OpenJDK)
RUN mkdir -p /opt/java && \
    curl -L https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.22+7/OpenJDK11U-jdk_x64_linux_hotspot_11.0.22_7.tar.gz \
    | tar -xz -C /opt/java --strip-components=1

# Instalar GeckoDriver (compatível com o Firefox)
RUN GECKODRIVER_VERSION=$(curl -sS https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep '"tag_name"' | cut -d '"' -f 4) && \
    wget -q -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ && \
    chmod +x /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Spark Download e instalação
RUN mkdir -p /opt/spark && \
    curl -sL https://dlcdn.apache.org/spark/spark-3.5.5/spark-3.5.5-bin-hadoop3.tgz | tar -xz -C /opt/spark --strip-components=1

#Variveis de ambiente Java e Spark
ENV JAVA_HOME=/opt/java
ENV SPARK_HOME=/opt/spark
ENV PATH="$JAVA_HOME/bin:$SPARK_HOME/bin:$PATH"
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=python3

# Voltano para o usuário airflow
USER airflow

# Instalar as dependências do requirements.txt
RUN pip install --no-cache-dir --no-build-isolation -r /opt/airflow/requirements.txt

RUN pip show pendulum

# Copiar a pasta raiz para o contêiner do Airflow
COPY . /opt/airflow/

#Definindo diretorio de trabalho
WORKDIR /opt/airflow

# Expondo a porta do Airflow
EXPOSE 8080

