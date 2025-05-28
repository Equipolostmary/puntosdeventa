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

# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")

    st.markdown('<div class="seccion">DATOS REGISTRADOS</div>', unsafe_allow_html=True)
    columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada") + 1])
    for col in columnas_visibles:
        if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
            etiqueta = "Usuario" if col.lower() == "usuario" else col
            st.markdown(f"**{etiqueta}:** {user.get(col, '')}")

    st.markdown('<div class="seccion">ESTADO DE PROMOCIONES</div>', unsafe_allow_html=True)
    total_promos = user.get("TOTAL PROMOS", 0)
    entregados = user.get("P", 0)  # Suponiendo que la columna P es la de entregados
    pendientes = user.get("Q", 0)  # Suponiendo que la columna Q es la de pendientes
    st.write(f"- TOTAL promociones acumuladas: {total_promos}")
    st.write(f"- Pendientes de entregar: {pendientes}")
    st.write(f"- Promos entregadas: {entregados}")

    st.markdown('<div class="seccion">SUBIR NUEVAS PROMOCIONES</div>', unsafe_allow_html=True)
    if "widget_key_promos" not in st.session_state:
        st.session_state.widget_key_promos = str(uuid.uuid4())
    if "widget_key_imgs" not in st.session_state:
        st.session_state.widget_key_imgs = str(uuid.uuid4())

    promo_tappo = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_tappo")
    promo_bm = st.number_input("Promos 3x21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_bm")
    imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

    if st.button("SUBIR PROMOCIONES"):
        if not imagenes:
            st.warning("Debes subir al menos una imagen.")
        else:
            try:
                carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
                service = conectar_drive(st.secrets["gcp_service_account"])
                for img in imagenes:
                    subir_archivo_a_drive(service, img, img.name, carpeta_id)

                row = user.name + 2
                col_tappo = df.columns.get_loc("Promos 2+1 TAPPO") + 1
                col_bm = df.columns.get_loc("Promos 3x21 BM1000") + 1
                actual_tappo = int(user.get("Promos 2+1 TAPPO", 0))
                actual_bm = int(user.get("Promos 3x21 BM1000", 0))
                worksheet.update_cell(row, col_tappo, str(actual_tappo + promo_tappo))
                worksheet.update_cell(row, col_bm, str(actual_bm + promo_bm))
                worksheet.update_cell(row, df.columns.get_loc("TOTAL PROMOS") + 1, str(total_promos + promo_tappo + promo_bm))

                st.success("Promociones subidas correctamente.")
                time.sleep(2)
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.rerun()
            except Exception as e:
                st.error(f"Error al subir promociones: {e}")

    st.markdown('<div class="seccion">REPORTA TUS VENTAS</div>', unsafe_allow_html=True)
    if "widget_key_ventas" not in st.session_state:
        st.session_state.widget_key_ventas = str(uuid.uuid4())
    if "widget_key_fotos" not in st.session_state:
        st.session_state.widget_key_fotos = str(uuid.uuid4())

    with st.form("formulario_ventas"):
        cantidad = st.number_input("Dispositivos vendidos este mes", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
        fotos = st.file_uploader("Sube fotos de ventas", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
        enviar = st.form_submit_button("Enviar")

    if enviar:
        if not fotos:
            st.warning("Debes subir al menos una imagen.")
        else:
            try:
                col_destino = "VENTAS MENSUALES"
                row = user.name + 2
                col_index = df.columns.get_loc(col_destino) + 1
                valor_anterior = int(user.get(col_destino, 0)) if str(user.get(col_destino, 0)).isdigit() else 0
                suma = valor_anterior + int(cantidad)
                worksheet.update_cell(row, col_index, str(suma))

                carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
                service = conectar_drive(st.secrets["gcp_service_account"])
                for archivo in fotos:
                    subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

                st.success("Ventas reportadas correctamente.")
                time.sleep(2)
                st.session_state.widget_key_ventas = str(uuid.uuid4())
                st.session_state.widget_key_fotos = str(uuid.uuid4())
                st.rerun()
            except Exception as e:
                st.error(f"Error al subir ventas: {e}")

    if correo_usuario == ADMIN_EMAIL:
        st.markdown('<div class="seccion">RESUMEN MAESTRO</div>', unsafe_allow_html=True)
        columnas_resumen = ["Usuario", "Contraseña", "Promos 2+1 TAPPO", "Promos 3x21 BM1000", "TOTAL PROMOS", "VENTAS MENSUALES"]
        columnas_presentes = [c for c in columnas_resumen if c in df.columns]
        resumen_df = df[columnas_presentes].fillna("")
        st.dataframe(resumen_df, use_container_width=True)
else:
    st.image("logo.png", use_container_width=True)
    correo = st.text_input("Usuario").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        user = buscar_usuario(correo)
        if not correo or not clave:
            st.warning("Debes completar ambos campos.")
        elif user is None:
            st.error("Usuario no encontrado.")
        else:
            pass_guardada = str(user.get("Contraseña", "")).strip().replace(",", "")
            pass_introducida = clave.strip().replace(",", "")
            if not pass_guardada:
                st.error("No hay contraseña configurada para este usuario.")
            elif pass_guardada != pass_introducida:
                st.error("Contraseña incorrecta.")
            else:
                st.session_state["auth_email"] = correo
                st.rerun()
