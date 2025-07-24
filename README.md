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
Configurando o PySpark no Windows 11

Para colocar o PySpark funcionando na sua máquina Windows 11, siga estes passos:

Pré-requisitos

    Spark: Baixe o Spark 3.5.0.

    Hadoop: Baixe o Hadoop 3.3.6.

    WinUtils: Baixe o WinUtils 3.3.6. (https://github.com/cdarlint/winutils/tree/master/hadoop-3.3.6/bin)

    JDK: Instale o JDK 11 ou superior.

Instalação
    
    Necessário WinRar ou outro programa parecido para extrair Spark e Hadoop
    
    Extraia o Spark: Extraia o arquivo Spark baixado para C:\spark. 

    Posicione o Hadoop: Mova o conteúdo do arquivo Hadoop baixado para uma nova pasta: C:\spark\hadoop\.

    Adicione o WinUtils: Coloque o arquivo winutils.exe (do download do WinUtils) dentro de C:\spark\hadoop\bin\.
</div>



# Configurando variaveis
✅ 1. Abra a tela de variáveis de ambiente:

    Pressione Win + S e digite "variáveis de ambiente".

    Clique em "Editar variáveis de ambiente do sistema".

    Na janela que abrir, clique em "Variáveis de Ambiente..." no canto inferior direito.
    
✅ 2. Crie as variáveis do sistema (parte inferior):

    Clique em "Nova..." em "Variáveis de sistema" e adicione as seguintes:
    
    JAVA_HOME = C:\Program Files\Java\jdk-11
    SPARK_HOME = C:\spark
    HADOOP_HOME = C:\spark\hadoop

    *Obs caso tenha instalado em locais diferentes, ajustar de acordo. Para confirmar o diretório clique no botão 'Procurar no Diretório'
    

✅ 3. Edite a variável Path:

    Ainda em "Variáveis de sistema", encontre a variável chamada Path.

    Clique em *Editar*.

    Clique em Novo e adicione:

    %JAVA_HOME%\bin
    %SPARK_HOME%\bin
    %HADOOP_HOME%\bin  

✅ 5. Teste se tudo está funcionando:
    
    Abra o Prompt de Comando (cmd) e digite:
    
    echo %JAVA_HOME%
    echo %SPARK_HOME%
    echo %HADOOP_HOME%
    winutils.exe ls
    pyspark
## Problemas ao instalar pyspark
Foi necessário instalar Rust
https://rustup.rs/

