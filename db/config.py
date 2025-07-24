import os

# Configurações do banco de dados
DB_CONFIG = {
    "host": "host.docker.internal" if os.environ.get("DOCKER") == "true" else "localhost",
    "port": 5432,
    "database": "farfetch",
    "user": "postgres",
    "password": "123456"
}

# Nome da tabela
TABLE_NAME = "promocoes_jaquetas"

# Caminhos dos arquivos
PASTA_BRUTO = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/bruto"
PASTA_TRATADO = "C:/Users/JPA/Desktop/Projetos/Selenium/projeto_selenium/dados/tratado"