import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ======== ESTILO VISUAL GENERAL ========
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
.logo-container {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    margin-bottom: 10px;
}
.logo-frame {
    background-color: white;
    padding: 10px;
    border-radius: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    width: 60%;
    max-width: 600px;
    margin: auto;
}
.titulo {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: black;
    margin: 20px 0 10px 0;
    background-color: #cdb4f5;
    padding: 10px;
    border-radius: 10px;
}
.seccion {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-top: 30px;
    margin-bottom: 10px;
    border-bottom: 2px solid #bbb;
    padding-bottom: 5px;
}
button[kind="primary"] {
    font-family: 'Montserrat', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ============ AUTENTICACIÓN Y DATOS ============
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

enlaces = {
    "ACCIONES COMERCIALES Q4 2024": "https://docs.google.com/spreadsheets/d/1DqC1348Z3LqnzCVB8d8AqDbsAR3WUDUf/edit?gid=1142706501#gid=1142706501",
    "CATALOGO DE MATERIALES": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-XPpyn22EL6G/p/10ciZH8DpEsC5GNpYSigFrfJ_Fln9B0Q2/preview?authuser=0"
}
# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    if correo_usuario == ADMIN_EMAIL:
        st.markdown(f'<div class="titulo">ÁREA PRIVADA – ADMINISTRADOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="seccion">ACCESO A RECURSOS</div>', unsafe_allow_html=True)
        opcion = st.selectbox("Selecciona un recurso para abrir:", sorted(enlaces.keys()), key=str(uuid.uuid4()))
        if opcion:
            st.markdown(f"[Abrir {opcion} ▶️]({enlaces[opcion]})", unsafe_allow_html=True)

    else:
        user = buscar_usuario(correo_usuario)
        if user is None:
            st.error("Usuario no encontrado.")
            st.session_state.clear()
            st.rerun()

        nombre_usuario = user["Expendiduría"]
        st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)
        st.success(f"¡Bienvenido, {nombre_usuario}!")

        st.markdown('<div class="seccion">DATOS REGISTRADOS</div>', unsafe_allow_html=True)
        columnas_visibles = ["Usuario", "Expendiduría", "Dirección", "Código postal", "POBLACION", "PROVINCIA", "TELÉFONO", "Nombre", "RESPONSABLE DE ZONA"]
        for col in columnas_visibles:
            st.markdown(f"**{col}:** {user.get(col, '')}")

        st.markdown('<div class="seccion">ESTADO DE PROMOCIONES</div>', unsafe_allow_html=True)
        def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
        tappo = val("Promoción 2+1 TAPPO")
        bm1000 = val("Promoción 3×21 BM1000")
        total = val("TOTAL PROMOS")
        entregados = val("REPUESTOS") if "REPUESTOS" in df.columns else 0
        pendientes = val("PENDIENTE DE REPONER") if "PENDIENTE DE REPONER" in df.columns else 0

        st.write(f"- TAPPO asignados: {tappo}")
        st.write(f"- BM1000 asignados: {bm1000}")
        st.write(f"- Total promociones acumuladas: {total}")
        st.write(f"- Promos entregadas: {entregados}")
        st.write(f"- Pendientes de entregar: {pendientes}")

        st.markdown('<div class="seccion">SUBIR NUEVAS PROMOCIONES</div>', unsafe_allow_html=True)
        promo1 = st.number_input("Promos 2+1 TAPPO", min_value=0)
        promo2 = st.number_input("Promos 3×21 BM1000", min_value=0)
        imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png"], accept_multiple_files=True)

        if st.button("SUBIR PROMOCIONES"):
            if not imagenes:
                st.warning("Selecciona al menos una imagen.")
            else:
                service = conectar_drive(st.secrets["gcp_service_account"])
                carpeta_id = user["Carpeta privada"].split("/")[-1]
                for img in imagenes:
                    subir_archivo_a_drive(service, img, img.name, carpeta_id)
                row = user.name + 2
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO") + 1, str(tappo + promo1))
                worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000") + 1, str(bm1000 + promo2))
                worksheet.update_cell(row, df.columns.get_loc("TOTAL PROMOS") + 1, str(tappo + promo1 + bm1000 + promo2))
                st.success("✅ Imágenes subidas y promociones actualizadas.")
                time.sleep(2)
                st.rerun()

        st.markdown('<div class="seccion">INCENTIVO COMPENSACIONES MENSUALES</div>', unsafe_allow_html=True)
        objetivo = user.get("OBJETIVO", "")
        compensacion = user.get("COMPENSACION", "")
        ventas_mensuales = user.get("VENTAS MENSUALES", "")
        st.write(f"- OBJETIVO: {objetivo if objetivo else '*No asignado*'}")
        st.write(f"- COMPENSACIÓN: {compensacion if compensacion else '*No definido*'}")
        st.write(f"- Ventas acumuladas: {ventas_mensuales if ventas_mensuales else '*Sin registrar*'}")

        st.markdown('<div class="seccion">REPORTA TUS VENTAS</div>', unsafe_allow_html=True)
        ventas = st.number_input("¿Cuántos dispositivos has vendido este mes?", min_value=0)
        fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True)

        if st.button("Enviar ventas"):
            if not fotos:
                st.warning("Debes subir al menos una imagen.")
            else:
                row = user.name + 2
                col = df.columns.get_loc("VENTAS MENSUALES") + 1
                anterior = int(user.get("VENTAS MENSUALES", 0)) if str(user.get("VENTAS MENSUALES", 0)).isdigit() else 0
                worksheet.update_cell(row, col, str(anterior + ventas))
                carpeta_id = user["Carpeta privada"].split("/")[-1]
                service = conectar_drive(st.secrets["gcp_service_account"])
                for archivo in fotos:
                    subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)
                st.success("✅ Ventas registradas correctamente.")
                time.sleep(2)
                st.rerun()

else:
    st.image("logo.png", use_container_width=True)
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        user = buscar_usuario(correo)
        if not correo or not clave:
            st.warning("Debes completar ambos campos.")
        elif user is None:
            st.error("Correo no encontrado.")
        else:
            if str(user.get("Contraseña", "")).strip() == clave.strip():
                st.session_state["auth_email"] = correo
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
