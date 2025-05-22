import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread

# Conexión a Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["sheet_id"])
worksheet = sheet.sheet1
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Configuración visual
st.set_page_config(page_title="Puntos de Venta", layout="centered")
st.markdown(""" 
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
[data-testid="stAppViewContainer"] > .main {
    background-color: #E9D5FF;
}
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# Logo centrado
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("logo.png", use_column_width=True)

st.title("Iniciar sesión")

# Función para encontrar usuario
def encontrar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    if mask.any():
        return df[mask].iloc[0]
    return None

# Manejo de sesión
if "auth_email" not in st.session_state:
    st.session_state.auth_email = None

if st.session_state.auth_email:
    st.success(f"Sesión iniciada: {st.session_state.auth_email}")
    st.write("Aquí va el panel privado del usuario.")
else:
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if not correo or not clave:
            st.warning("Por favor, rellena todos los campos.")
        else:
            usuario = encontrar_usuario(correo)
            if usuario is None:
                st.error("Correo no encontrado.")
            elif "Contraseña" not in usuario or str(usuario["Contraseña"]).strip() == "":
                st.error("Este usuario no tiene contraseña configurada.")
            elif str(usuario["Contraseña"]).strip() != clave:
                st.error("Contraseña incorrecta.")
            else:
                st.session_state.auth_email = correo
                st.experimental_rerun()
