<div align="center">
  <h1>Projeto Selenium</h1>
  
</div>
<br>
Sistema analítico, com login, com dashboard de produtos extraidos com Selenium, em Python usando Streamlit e PySpark para o ETL.

Realizado o web scrapping com selenium no site da Farfetch, ele entra no site depois vai em promoções e depois na sessão de jaquetas, feito um sistema em Streamlit com botão para executar o scrapping e um dash interativo também para insights dos dados gerados.
## Ferramentas
- Python
- Selenium
- Streamlit
- Pandas
- Spark


## Funções
- Scraping de produtos
- ETL com Spark e Pandas
- Dash e painel com Streamlit
- CSV e Parquet
  
<div align="center">
    <img src="https://github.com/user-attachments/assets/92732e5f-a921-4a87-9471-585020ceded3" alt="dash1" width="450"/>
    <img src="https://github.com/user-attachments/assets/4560195f-544d-4d65-8a6e-2bacc8f864d8" alt="dash2" width="450"/>
</div>

## Requirements
- Python 3.12
- `streamlit` - plataforma web
- `pandas` - manipulação de dados
- `psycopg2` - conexao com postgre
- `schedule` - agendamento de tarefas
Utilizando PySpark no Windows 11
Baixar: spark 3.5.0 > ; hadoop 3.3.6 ; winutils 3.3.6 ; jdk 11 >
Extrair o spark no c:/spark, colocar o hadoop no c:/spark/hadoop/ , o winutils dentro do bin do hadoop e configurar as variaveis de ambiente do Windows, JAVA_HOME, SPARK_HOME, PYSPARK_HOME, HADOOP_HOME.
