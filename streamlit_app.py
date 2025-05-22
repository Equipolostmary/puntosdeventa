import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid

st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")

ADMIN_EMAIL = "equipolostmary@gmail.com"

# ✅ Estilos visuales y fondo lila
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #e6e0f8 !important;
    }
    .barra {
        background-color: white;
        color: #5a3a8a;
        font-size: 20px;
        font-weight: bold;
        padding: 16px;
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 1000;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .espaciado {
        margin-top: 80px;
    }
    </style>
""", unsafe_allow_html=True)

# 🔐 Mostrar barra si está logueado
nombre_usuario = ""
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    nombre_usuario = correo_usuario
    # extraemos el nombre real desde la hoja
    def buscar_usuario(email):
        mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
        return df[mask].iloc[0] if mask.any() else None

    # Conectamos a Google
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
    worksheet = sheet.worksheet("Registro")
    df = pd.DataFrame(worksheet.get_all_records())
    user = buscar_usuario(correo_usuario)
    if user is not None:
        nombre_usuario = user["Expendiduría"]

    # BARRA con botón nativo
    st.markdown(f"<div class='barra'>ÁREA PRIVADA – {nombre_usuario}  <span></span></div>", unsafe_allow_html=True)
    st.markdown("<div class='espaciado'></div>", unsafe_allow_html=True)
    if st.button("Cerrar sesión", key="cerrar_sesion"):
        st.session_state.clear()
        st.rerun()
else:
    # si no está logueado, solo mostramos logo
    st.image("logo.png", use_container_width=True)

# 🔑 LOGIN
if "auth_email" not in st.session_state:
    st.image("logo.png", use_container_width=True)
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        # reconectamos hoja
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
        worksheet = sheet.worksheet("Registro")
        df = pd.DataFrame(worksheet.get_all_records())

        def buscar_usuario(email):
            mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
            return df[mask].iloc[0] if mask.any() else None

        if not correo or not clave:
            st.warning("Debes completar ambos campos.")
        else:
            user = buscar_usuario(correo)
            if user is None:
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

# 💼 ZONA PRIVADA
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")
    st.subheader("📋 Tus datos personales")

    columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
    for col in columnas_visibles:
        if str(col).lower() not in ["contraseña", "correo", "correo electrónico", "dirección de correo electrónico"]:
            st.markdown(f"**{col}:** {user.get(col, '')}")

    st.subheader("📦 Estado de promociones")

    def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
    tappo_asig = val("Promoción 2+1 TAPPO")
    tappo_ent = val("Entregados promo TAPPO")
    tappo_falt = val("Falta por entregar TAPPO")
    bm_asig = val("Promoción 3×21 BM1000")
    bm_ent = val("Entregados promo BM1000")
    bm_falt = val("Falta por entregar BM1000")

    st.markdown(f"""
    - **TAPPO asignados:** {tappo_asig} | ✅ Entregados: {tappo_ent} | ⏳ Pendientes: {tappo_falt}
    - **BM1000 asignados:** {bm_asig} | ✅ Entregados: {bm_ent} | ⏳ Pendientes: {bm_falt}
    - 🕓 **Última actualización:** {user.get('Última actualización', 'N/A')}
    """)

    if st.session_state.get("subida_ok"):
        st.success("✅ Imágenes subidas correctamente. Contadores actualizados.")
        time.sleep(2)
        st.session_state.pop("subida_ok")
        st.rerun()

    if "widget_key_promos" not in st.session_state:
        st.session_state.widget_key_promos = str(uuid.uuid4())
    if "widget_key_imgs" not in st.session_state:
        st.session_state.widget_key_imgs = str(uuid.uuid4())

    st.subheader("📸 Subir nuevas promociones")
    promo1 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
    promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
    imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

    if st.button("Subir promociones"):
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
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(tappo_asig + promo1))
                worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(bm_asig + promo2))
                worksheet.update_cell(row, df.columns.get_loc("Última actualización")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state["subida_ok"] = True
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.rerun()

    if correo_usuario == ADMIN_EMAIL:
        st.subheader("📊 Vista completa de todos los puntos")
        columnas = [
            "Expendiduría", "Dirección de correo electrónico", "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "Entregados promo TAPPO", "Entregados promo BM1000",
            "Falta por entregar TAPPO", "Falta por entregar BM1000",
            "Última actualización"
        ]
        st.dataframe(df[columnas].fillna(0), use_container_width=True)
