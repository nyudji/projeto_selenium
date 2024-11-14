from selenium import webdriver
import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

def run_scraping():
    # Abre o navegador
    nav = webdriver.Firefox()
    url = 'https://www.farfetch.com/br/shopping/men/items.aspx'
    nav.get(url)
    print('Acessando o link:', url)
    time.sleep(3)
    nav.maximize_window()

    wait = WebDriverWait(nav, 15)
    sale_menu = wait.until(EC.visibility_of_element_located((By.XPATH, "//a[@data-nav='Sale']")))
    actions = ActionChains(nav)
    actions.move_to_element(sale_menu).perform()
    time.sleep(2)

    try:
        jackets_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ewmv8150') and text()='Jackets']")))
        jackets_link.click()
        print("Entrou no menu de Jaquetas!")
    except Exception as e:
        print("Erro ao clicar em Jaquetas:", e)
        nav.quit()

    time.sleep(5)

    produtos_lista = []

    def rolar_pagina():
        nav.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    total_produtos = 0
    while True:
        produtos = nav.find_elements(By.XPATH, '//p[@data-component="ProductCardDescription"]')
        marcas = nav.find_elements(By.XPATH, '//p[@data-component="ProductCardBrandName"]')
        precos = nav.find_elements(By.XPATH, '//p[@data-component="PriceFinal"]')
        precos_og = nav.find_elements(By.XPATH, '//p[@data-component="PriceOriginal"]')
        precos_disc = nav.find_elements(By.XPATH, '//p[@data-component="PriceDiscount"]')

        if len(produtos) == total_produtos:
            break
        total_produtos = len(produtos)

        # Certifique-se de que a coleta comece desde o primeiro item
        for produto, marca, preco, preco_og, preco_disc in zip(produtos, marcas, precos, precos_og, precos_disc):
            try:
                produto_nome = produto.text
                nav.execute_script("arguments[0].scrollIntoView();", produto)
                time.sleep(1)
                ActionChains(nav).move_to_element(produto).perform()
                produtos_lista.append({
                    "Produto": produto_nome,
                    "Marca": marca.text,
                    "Preço": preco.text,
                    "Preço Original": preco_og.text,
                    "Desconto": preco_disc.text
                })
            except Exception as e:
                print(f"Erro ao processar o produto: {e}")


    df_produtos = pd.DataFrame(produtos_lista)

    data_atual = datetime.now().strftime("%d%m%Y")
    pasta_base = os.path.join("dados", "bruto")
    os.makedirs(pasta_base, exist_ok=True)
    nome_arquivo = f"promocoes_jaquetas_{data_atual}.csv"
    caminho_completo = os.path.join(pasta_base, nome_arquivo)
    df_produtos.to_csv(caminho_completo, index=False, encoding='utf-8')
    print("Dados salvos em CSV com sucesso.")

    nav.quit()
