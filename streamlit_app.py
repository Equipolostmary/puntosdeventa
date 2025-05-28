import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
html, body, .block-container, .stApp {
    background-color: #e6e0f8 !important;
    font-family: 'Montserrat', sans-serif;
}
section[data-testid="stSidebar"], #MainMenu, header, footer {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# Autenticación
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

# Leer solo primeras filas para test
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records()).head(100)

def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

enlaces = {
    "ACCIONES COMERCIALES Q4 2024": "https://docs.google.com/spreadsheets/d/1DqC1348Z3LqnzCVB8d8AqDbsAR3WUDUf/edit?gid=1142706501#gid=1142706501",
    "CATALOGO DE MATERIALES": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-XPpyn22EL6G/p/10ciZH8DpEsC5GNpYSigFrfJ_Fln9B0Q2/preview?authuser=0"
}

if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    if correo_usuario == ADMIN_EMAIL:
        st.markdown("## Área del administrador")
        opcion = st.selectbox("Selecciona un recurso:", sorted(enlaces.keys()))
        if opcion:
            st.markdown(f"[Ir al recurso seleccionado]({enlaces[opcion]})", unsafe_allow_html=True)
    else:
        if user is not None:
            st.markdown(f"## Bienvenido: {user.get('Expendiduría', correo_usuario)}")
        else:
            st.error("Usuario no encontrado")
            st.session_state.clear()
            st.rerun()
else:
    st.warning("Por favor, inicia sesión primero.")
