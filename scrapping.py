from selenium import webdriver
import time
import pandas as pd
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from tratamento import tratamento

def run_scraping():
    # Abre o navegador
    try:
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
            nav.refresh()
            jackets_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class, 'ewmv8150') and text()='Jackets']")))
            jackets_link.click()
            nav.quit()

        time.sleep(5)

        produtos_lista = []

        def rolar_pagina():
            # Salva a altura da página antes de rolar
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
            print('Total produtos:',total_produtos)
            for i in range(len(produtos)):
                try:
                    produto_nome = produtos[i].text if produtos[i] else "Nome não encontrado"
                    marca_nome = marcas[i].text if i < len(marcas) and marcas[i] else "Marca não encontrada"
                    preco_final = precos[i].text if i < len(precos) and precos[i] else "Preço indisponível"
                    preco_original = precos_og[i].text if i < len(precos_og) and precos_og[i] else "Original não disponível"                    

                    produtos_lista.append({
                        "Produto": produto_nome,
                        "Marca": marca_nome,
                        "Preço": preco_final,
                        "Preço Original": preco_original
                    })
                    time.sleep(1)
                except Exception as e:
                    print(f"Erro ao processar o produto {i}: {e}")
                finally:
                    print(f"Produto: {i} processado")

    except Exception as e:
        print(f"Erro ao fazer o scrapping: {e}")

    if not produtos_lista:
        print("Erro: Nenhum produto encontrado para salvar. O scraping pode ter falhado.")
    else:
        # Cria o DataFrame e salva os dados em um arquivo CSV
        df_produtos = pd.DataFrame(produtos_lista)
        data_atual = datetime.now().strftime("%d%m%Y")
        pasta_base = os.path.join("dados", "bruto")
        os.makedirs(pasta_base, exist_ok=True)
        nome_arquivo = f"promocoes_jaquetas_{data_atual}.csv"
        caminho_completo = os.path.join(pasta_base, nome_arquivo)
        df_produtos.to_csv(caminho_completo, index=False, encoding='utf-8')
        print('Tratamento iniciado')
        tratamento()
        print('Tratamento Finalizado')
        print("WebScrapping feito e dados salvos em CSV com sucesso.")    
