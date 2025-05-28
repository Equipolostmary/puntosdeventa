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

if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    user = buscar_usuario(correo_usuario)
    if correo_usuario != ADMIN_EMAIL:
        nombre_usuario = user.get("Expendiduría", correo_usuario)
        st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)
        st.success(f"¡Bienvenido, {nombre_usuario}!")
    else:
        st.markdown(f'<div class="titulo">ÁREA PRIVADA</div>', unsafe_allow_html=True)

    if correo_usuario == ADMIN_EMAIL:
        st.markdown('<div class="seccion">🔎 BUSCAR Y EDITAR PUNTOS DE VENTA</div>', unsafe_allow_html=True)
        termino = st.text_input("Buscar por teléfono, correo, expendiduría o usuario").strip().lower()

        if termino:
            resultados = df[df.apply(lambda row: termino in str(row.get("TELÉFONO", "")).lower()
                                                or termino in str(row.get("Usuario", "")).lower()
                                                or termino in str(row.get("Expendiduría", "")).lower(), axis=1)]
            if not resultados.empty:
                opciones = [f"{row['Usuario']} - {row['Expendiduría']} - {row['TELÉFONO']}" for _, row in resultados.iterrows()]
                seleccion = st.selectbox("Selecciona un punto para editar:", opciones, key="buscador_admin")
                index = resultados.index[opciones.index(seleccion)]
                with st.form(f"editar_usuario_{index}"):
                    nuevos_valores = {}
                    for col in df.columns:
                        if col != "Carpeta privada":
                            nuevos_valores[col] = st.text_input(col, str(df.at[index, col]), key=f"{col}_{index}")
                    guardar = st.form_submit_button("Guardar cambios")
                    if guardar:
                        try:
                            for col, nuevo_valor in nuevos_valores.items():
                                worksheet.update_cell(index + 2, df.columns.get_loc(col) + 1, nuevo_valor)
                            st.success("✅ Datos actualizados correctamente.")
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")
            else:
                st.warning("No se encontró ningún punto con ese dato.")

    else:
        if user is None:
            st.error("Usuario no encontrado.")
            st.session_state.clear()
            st.rerun()

        st.markdown('<div class="seccion">SUBIR NUEVAS PROMOCIONES</div>', unsafe_allow_html=True)
        if "widget_key_promos" not in st.session_state:
            st.session_state.widget_key_promos = str(uuid.uuid4())
        if "widget_key_imgs" not in st.session_state:
            st.session_state.widget_key_imgs = str(uuid.uuid4())

        tappo = int(user.get("Promoción 3x10 TAPPO", 0)) if str(user.get("Promoción 3x10 TAPPO", 0)).isdigit() else 0
        bm1000 = int(user.get("Promoción 3×21 BM1000", 0)) if str(user.get("Promoción 3×21 BM1000", 0)).isdigit() else 0

        promo1 = st.number_input("Promos 3x10 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
        promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
        imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

        if st.button("SUBIR PROMOCIONES"):
            if not imagenes:
                st.warning("Selecciona al menos una imagen.")
            else:
                service = conectar_drive(st.secrets["gcp_service_account"])
                carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
                ok = 0
                for img in imagenes:
                    try:
                        subir_archivo_a_drive(service, img, img.name, carpeta_id)
                        ok += 1
                    except Exception as e:
                        st.error(f"Error al subir {img.name}: {e}")
                if ok:
                    row = user.name + 2
                    worksheet.update_cell(row, df.columns.get_loc("Promoción 3x10 TAPPO") + 1, str(tappo + promo1))
                    worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000") + 1, str(bm1000 + promo2))
                    worksheet.update_cell(row, df.columns.get_loc("TOTAL PROMOS") + 1, str(tappo + promo1 + bm1000 + promo2))
                    st.session_state.widget_key_promos = str(uuid.uuid4())
                    st.session_state.widget_key_imgs = str(uuid.uuid4())
                    st.success("✅ Imágenes subidas correctamente. Contadores actualizados.")
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
            password_guardada = str(user.get("Contraseña", "")).strip().replace(",", "")
            password_introducida = clave.strip().replace(",", "")
            if not password_guardada:
                st.error("No hay contraseña configurada para este usuario.")
            elif password_guardada != password_introducida:
                st.error("Contraseña incorrecta.")
            else:
                st.session_state["auth_email"] = correo
                st.rerun()
