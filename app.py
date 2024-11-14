import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from scrapping import run_scraping  # Função do scraper
from dash import display_dashboard  # Função para mostrar o dashboard
import threading
import time

# Carregar as configurações do arquivo YAML
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Autenticação de usuário
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

if st.session_state["authentication_status"]:
    authenticator.logout()
    st.write(f'Bem Vindo *{st.session_state["name"]}*')
    st.title('Página de Sistema')

    # Inicializar a chave de progresso no session_state
    if "scraping_in_progress" not in st.session_state:
        st.session_state.scraping_in_progress = False

    if st.button('Executar Scrapping'):
        progress_bar = st.progress(0)
        
        # Iniciar o scraping em uma thread separada
        if not st.session_state.scraping_in_progress:
            st.session_state.scraping_in_progress = True
            thread = threading.Thread(target=run_scraping)
            thread.start()

            try:
                # Atualizar a barra de progresso enquanto a thread estiver em execução
                while thread.is_alive():
                    try:
                        current_progress = float(progress_bar.progress())  # Tentar a conversão para float
                    except TypeError:
                        current_progress = 0
                    new_progress = current_progress + 0.15
                    progress_bar.progress(new_progress)
                    time.sleep(0.1)
            except Exception as e:
                # Exibir o erro na interface e resetar o estado do scraping
                st.error(f"Ocorreu um erro durante o scraping: {e}")
                st.session_state.scraping_in_progress = False
                progress_bar.progress(0)  # Resetar a barra de progresso
            else:
                # Caso o scraping seja concluído sem erro
                st.success("Scraping concluído com sucesso!")
                new_progress = current_progress + 0.5
                progress_bar.progress(new_progress)
            finally:
                # Resetar o estado do scraping
                st.session_state.scraping_in_progress = False
                progress_bar.progress(0)  # Resetar a barra de progresso

        # Exibir o dashboard após o scraping
        display_dashboard()

elif st.session_state["authentication_status"] is False:
    st.error('Usuário/Senha inválido')
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, utilize seu usuário e senha!')
