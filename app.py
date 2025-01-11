import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from scrapping import run_scraping  # Função do scraper
from dash import display_dashboard, display_dash2  # Função para mostrar o dashboard
import threading
import time

def atualizar_dashboard():
    st.rerun()

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

# Verificar se o usuário está autenticado
if st.session_state["authentication_status"]:
    col1, col2, col3 = st.columns([1.5, 2, 1]) 
    with col1:
        st.write(f'Bem Vindo *{st.session_state["name"]}*')
    with col3:
        authenticator.logout()
    
    st.sidebar.markdown("### Projeto Selenium:")
    # Navegação entre as páginas
    page = st.sidebar.radio("Escolha uma página", ("Scraping", "Dashboard"))

    # Inicializar a chave de progresso no session_state
    if "scraping_in_progress" not in st.session_state:
        st.session_state.scraping_in_progress = False

    # Página de Scraping
    if page == "Scraping":
        with col2:
            st.title('Página de Scraping')    
        with col1:
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
                            for i in range(100):
                                # Lógica do seu scraping aqui
                                time.sleep(0.25)  # Simula o tempo de scraping

                                # Atualiza o progresso
                                progress_bar.progress(i + 1)  # 'i + 1' para refletir o progresso de 1 a 100

                            # Após o término do scraping
                        st.success("Scraping finalizado!")
                        progress_bar.progress(0)
                    except Exception as e:
                        # Exibir o erro na interface e resetar o estado do scraping
                        st.error(f"Ocorreu um erro durante o scraping: {e}")
                        time.sleep(5)
                        st.session_state.scraping_in_progress = False
                        progress_bar.progress(0)  # Resetar a barra de progresso
                    finally:
                        # Resetar o estado do scraping
                        st.session_state.scraping_in_progress = False
                        progress_bar.progress(0)  # Resetar a barra de progresso
                        atualizar_dashboard()
        st.subheader('Ultimo scrapping feito')
        display_dashboard()
    # Página de Dashboard
    elif page == "Dashboard":
        with col2:
            st.title('Dashboard')
        display_dash2()
        # Exibir o dashboard após o scraping
        

elif st.session_state["authentication_status"] is False:
    st.error('Usuário/Senha inválido')
elif st.session_state["authentication_status"] is None:
    st.warning('Por favor, utilize seu usuário e senha!')
