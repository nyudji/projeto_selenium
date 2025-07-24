<div align="center">
  <h1>Projeto Selenium</h1>
  
</div>
<br>
Este projeto foi desenvolvido com o objetivo de aprimorar meus conhecimentos em Web Scraping, ETL e DataViz. Utilizo Selenium para automatizar a extração de ofertas de jaquetas na seção de promoções do site da Farfetch, faço a Extração/Tratamento/Carregamento com PySpark e Pandas e depois salvando no PostgreSQL. Com Docker e Airflow fiz uma dag de scraping mensal. Por final uma visualização no Streamlit.

## Scrapping
- Entra no site da Farfetch
- Entra na seções de promoções de jaquetas
- Pega os produtos
- Realiza o Tratamento
- Salva em CSV, Parquet e SQL os dados brutos e tratados
- Visualização Interativa no Streamlit
  
<div align="center">
    <img src="https://github.com/user-attachments/assets/3db4877a-0fc8-4724-b9c0-bbc64101d33a" alt="image">
</div>

 ## Dados
- Produto
- Marca
- Preço Original
- Preço com desconto

 ## Dados tratados
- Data e Hora
- Desconto
- Categoria Preço
- Classificação Produto
- Acima ou abaixo do preço médio

## Funções
- Login Streamlit
- Scraping de produtos
- ETL com Spark e Pandas
- Dash e Painel com Streamlit
- CSV e Parquet
  
<div align="center">
    <img src="https://github.com/user-attachments/assets/372b5a2e-84b3-4521-afa1-9c2b99dd9b71" alt="image">
</div>

 ## Ferramentas
- Python
- Selenium
- Streamlit
- Pandas
- Spark
- PostgreSQL

## Implementações futuras
- Relatório com IA


## Requirements
- Python 3.12
- `streamlit` 
- `pandas`
- `selenium` 
- `pyspark` 

<div align="center">
<h1>Utilizando PySpark no Windows 11</h1>
Baixar: spark 3.5.0 > ; hadoop 3.3.6 ; winutils 3.3.6 ; jdk 11 >
Extrair o spark no c:/spark, colocar o hadoop no c:/spark/hadoop/ , o winutils dentro do bin do hadoop e configurar as variaveis de ambiente do Windows, JAVA_HOME, SPARK_HOME, PYSPARK_HOME, HADOOP_HOME.
</div>

## Problemas ao instalar pyspark
Foi necessário instalar Rust
https://rustup.rs/

