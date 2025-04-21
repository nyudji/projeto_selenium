from selenium import webdriver
import time
import pandas as pd
import os
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from tratamento import tratamento

# Configura logs para Airflow
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_scraping():
    nav = None
    produtos_lista = []

    try:
        # Apenas no Docker/Linux
        os.system("Xvfb :99 -screen 0 1920x1080x24 &")
        os.environ["DISPLAY"] = ":99"

        # Configura Firefox headless
        options = Options()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        nav = webdriver.Firefox(options=options)

        url = 'https://www.farfetch.com/br/shopping/men/items.aspx'
        nav.get(url)
        logging.info(f"Acessando o link: {url}")
        time.sleep(3)

        wait = WebDriverWait(nav, 15)

        # Hover via JavaScript (mais confiável em headless)
        nav.execute_script("""
            let sale = document.querySelector("a[data-nav='Sale']");
            if (sale) {
                sale.dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));
            }
        """)
        time.sleep(2)

        try:
            jackets_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ewmv8150') and text()='Jackets']")))
            nav.execute_script("arguments[0].scrollIntoView(true);", jackets_link)
            time.sleep(1)
            nav.execute_script("arguments[0].click();", jackets_link)
            logging.info("Clicou no menu de Jaquetas via JavaScript")
        except Exception as e:
            logging.warning(f"Erro ao clicar em Jaquetas: {e}")
            nav.refresh()

        time.sleep(5)

        def rolar_pagina():
            nav.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        total_produtos = 0
        while True:
            rolar_pagina()
            produtos = nav.find_elements(By.XPATH, '//p[@data-component="ProductCardDescription"]')
            marcas = nav.find_elements(By.XPATH, '//p[@data-component="ProductCardBrandName"]')
            precos = nav.find_elements(By.XPATH, '//p[@data-component="PriceFinal"]')
            precos_og = nav.find_elements(By.XPATH, '//p[@data-component="PriceOriginal"]')

            if len(produtos) == total_produtos:
                break
            total_produtos = len(produtos)
            logging.info(f"Total de produtos: {total_produtos}")

            for i in range(len(produtos)):
                try:
                    produtos_lista.append({
                        "Produto": produtos[i].text if produtos[i] else "Nome não encontrado",
                        "Marca": marcas[i].text if i < len(marcas) else "Marca não encontrada",
                        "Preço": precos[i].text if i < len(precos) else "Preço indisponível",
                        "Preço Original": precos_og[i].text if i < len(precos_og) else "Original não disponível"
                    })
                    print(produtos[i].text)
                    print(marcas[i].text)
                    time.sleep(1)
                except Exception as e:
                    logging.warning(f"Erro ao processar produto {i}: {e}")
                finally:
                    logging.info(f"Produto {i} processado")

    except Exception as e:
        logging.error(f"Erro geral no scraping: {e}")

    finally:
        if nav:
            nav.quit()

    if not produtos_lista:
        logging.warning("Nenhum produto coletado.")
        return

    def salvar_dados(produtos_lista):
        df = pd.DataFrame(produtos_lista)
        data_atual = datetime.now().strftime("%d%m%Y")
        pasta_base = "/opt/airflow/dados/bruto"
        os.makedirs(pasta_base, exist_ok=True)

        nome_arquivo = f"promocoes_jaquetas_{data_atual}.csv"
        caminho = os.path.join(pasta_base, nome_arquivo)

        contador = 1
        while os.path.exists(caminho):
            nome_arquivo = f"promocoes_jaquetas_{data_atual}_{contador}.csv"
            caminho = os.path.join(pasta_base, nome_arquivo)
            contador += 1

        df.to_csv(caminho, index=False, encoding='utf-8')
        logging.info(f"Dados salvos em: {caminho}")

        logging.info("Iniciando tratamento...")
        tratamento()
        logging.info("Tratamento finalizado.")

    salvar_dados(produtos_lista)

if __name__ == "__main__":
    run_scraping()
