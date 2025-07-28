# Nome do projeto/serviço principal
PROJECT_NAME=projeto_selenium
DOCKER_COMPOSE=docker-compose
PYTHON=python3

# 🔁 Builda os containers
build:
	$(DOCKER_COMPOSE) build --no-cache

# 🚀 Sobe os containers
up:
	$(DOCKER_COMPOSE) up -d

# 🧯 Derruba os containers
down:
	$(DOCKER_COMPOSE) down

# 🔄 Reinicia o serviço principal (web_app)
restart:
	$(DOCKER_COMPOSE) restart $(PROJECT_NAME)

# 🐚 Entra no container do app
bash:
	docker exec -it $(PROJECT_NAME) bash

# 🧪 Roda os testes (pytest)
test:
	pytest tests/

# 🎨 Formata o código com black
format:
	black src/

# 🧬 Instala dependências localmente
install:
	$(PYTHON) -m pip install -r requirements.txt

# 🛠️ Inicializa Airflow (caso precise executar antes do primeiro uso)
airflow-init:
	docker-compose run airflow-webserver airflow db init

# 🚦 Lista os logs do Airflow Webserver
logs:
	docker-compose logs -f airflow-webserver

streamlit:
	streamlit run src/app/main.py