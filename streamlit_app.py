import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
from datetime import datetime
from PIL import Image
import os

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(page_title="Zona Privada - Lost Mary", page_icon="📦", layout="centered")
st.markdown(
    '''
    <style>
    body {
        background-color: #f3e8ff;
    }
    .block-container {
        padding-top: 2rem;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# ---------- LOGO ----------
if os.path.exists("logo.png"):
    st.image("logo.png", width=400)

# ---------- AUTENTICACIÓN ----------
st.header("Iniciar sesión")
correo = st.text_input("Correo electrónico")
contraseña = st.text_input("Contraseña", type="password")
login_btn = st.button("Acceder")

if "sesion_iniciada" not in st.session_state:
    st.session_state.sesion_iniciada = False
    st.session_state.correo_usuario = ""

if login_btn:
    st.session_state.correo_usuario = correo.strip().lower()
    st.session_state.sesion_iniciada = True

if st.session_state.sesion_iniciada and st.session_state.correo_usuario:
    # ---------- CONEXIÓN CON GOOGLE SHEETS ----------
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    gcp_secrets = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(gcp_secrets, scopes=scope)
    client = gspread.authorize(creds)

    sheet_id = gcp_secrets["sheet_id"]
    sheet = client.open_by_key(sheet_id).worksheet("Registro")
    df = pd.DataFrame(sheet.get_all_records())

    # ---------- FILTRADO DE USUARIO ----------
    correo_usuario = st.session_state.correo_usuario
    punto = df[df["Dirección de correo electrónico"].str.lower() == correo_usuario]

    if punto.empty:
        st.error("Correo no registrado.")
    else:
        punto = punto.iloc[0]
        stored_password = str(punto.get("Contraseña", "")).strip()
        if stored_password != contraseña:
            st.error("Contraseña incorrecta.")
        else:
            # ---------- ZONA PRIVADA ----------
            st.success(f"Bienvenido, {punto['Expendiduría']}")
            st.markdown("### 📦 Estado de promociones")

            def safe_int(val):
                try:
                    return int(val)
                except:
                    return 0

            tappo_asignado = safe_int(punto.get("Promoción 2+1 TAPPO", 0))
            bm_asignado = safe_int(punto.get("Promoción 3×21 BM1000", 0))
            tappo_entregado = safe_int(punto.get("Entregados promo TAPPO", 0))
            bm_entregado = safe_int(punto.get("Entregados promo BM1000", 0))
            tappo_faltan = safe_int(punto.get("FALTA POR ENTREGAR TAPPO", 0))
            bm_faltan = safe_int(punto.get("FALTA POR ENTREGAR BM1000", 0))
            ultima = punto.get("Última actualización", "")

            st.markdown(f"**TAPPO asignados:** {tappo_asignado} ✅ Entregados: {tappo_entregado} ⏳ Pendientes: {tappo_faltan}")
            st.markdown(f"**BM1000 asignados:** {bm_asignado} ✅ Entregados: {bm_entregado} ⏳ Pendientes: {bm_faltan}")
            st.markdown(f"🕒 **Última actualización:** {ultima}")

            # ---------- SUBIDA DE ARCHIVOS ----------
            st.markdown("---")
            st.markdown("### 📤 Subir promociones")
            uploaded_files = st.file_uploader("Selecciona imágenes o tickets", accept_multiple_files=True, type=["jpg", "png", "jpeg"])

            if uploaded_files:
                st.success(f"{len(uploaded_files)} archivo(s) cargado(s) correctamente.")
