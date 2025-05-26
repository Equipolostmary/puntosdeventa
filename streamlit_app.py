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
    html, body, .block-container, .stApp, .main {
        background-color: #e6e0f8 !important;
        font-family: 'Montserrat', sans-serif;
    }
    section[data-testid="stSidebar"], #MainMenu, header, footer {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

# Conectar con Google
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
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    with st.container():
        st.markdown(f"""
        <div style="background-color:#bda2e0;padding:15px 10px;text-align:center;
                    font-weight:bold;font-size:20px;color:black;border-radius:5px;">
            ÁREA PRIVADA – {nombre_usuario}
        </div>
        """, unsafe_allow_html=True)

    st.image("logo.png", use_container_width=True)

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

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
    - 🥓 **Última actualización:** {user.get('Ultima actualización', 'N/A')}
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
                col_actualizacion = [c for c in df.columns if "actualiz" in c.lower()][0]
                worksheet.update_cell(row, df.columns.get_loc(col_actualizacion)+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state["subida_ok"] = True
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.rerun()

    if correo_usuario == ADMIN_EMAIL:
        st.subheader("📈 Vista completa de todos los puntos")
        columnas = [
            "Expendiduría", "Dirección de correo electrónico", "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "Entregados promo TAPPO", "Entregados promo BM1000",
            "Falta por entregar TAPPO", "Falta por entregar BM1000",
            "Ultima actualización"
        ]
        st.dataframe(df[columnas].fillna(0), use_container_width=True)
    st.markdown("---")
    st.header("💰 Incentivo compensaciones mensuales")

    ventas_sheet = client.open_by_key("1CpHwmPrRYqqMtXrZBZV7-nQOeEH6Z-RWtpnT84ztVB0").worksheet("General")
    valores = ventas_sheet.get_all_values()
    df_ventas = pd.DataFrame(valores[1:], columns=valores[0])
    df_ventas.columns = df_ventas.columns.str.strip().str.upper()
    df_ventas["TELÉFONO"] = df_ventas["TELÉFONO"].astype(str).str.replace(" ", "").str.strip()
    df_ventas = df_ventas.fillna(method="ffill")

    telefono_usuario = str(user.get("Teléfono")).replace(" ", "").strip()
    fila_usuario = df_ventas[df_ventas["TELÉFONO"] == telefono_usuario]

    ventas_marzo = ventas_abril = ventas_mayo = ventas_junio = "No disponible"
    incentivo_texto = "No asignado"
    fila_index = None

    if not fila_usuario.empty:
        row_data = fila_usuario.iloc[0]
        fila_index = fila_usuario.index[0] + 2
        incentivo_texto = row_data.get("OBJETIVOS Y COMPENSACIONES", "No asignado")
        ventas_marzo = row_data.get("MARZO", "No disponible")
        ventas_abril = row_data.get("ABRIL", "No disponible")
        ventas_mayo = row_data.get("MAYO", "No disponible")
        ventas_junio = row_data.get("JUNIO", "No disponible")

    st.markdown(f"**🎯 Objetivo asignado:** {incentivo_texto}")
    st.markdown(f"**📊 Marzo:** {ventas_marzo}")
    st.markdown(f"**📊 Abril:** {ventas_abril}")
    st.markdown(f"**📊 Mayo:** {ventas_mayo}")
    st.markdown(f"**📊 Junio:** {ventas_junio}")

    st.subheader("📤 Reporta tus ventas del mes")

    if "widget_key_ventas" not in st.session_state:
        st.session_state.widget_key_ventas = str(uuid.uuid4())
    if "widget_key_fotos" not in st.session_state:
        st.session_state.widget_key_fotos = str(uuid.uuid4())

    with st.form("formulario_ventas"):
        mes = st.selectbox("Selecciona el mes", ["Mayo", "Junio"], key=st.session_state.widget_key_ventas + "_mes")
        cantidad = st.number_input("¿Cuántos dispositivos has vendido?", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
        fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
        enviar = st.form_submit_button("Enviar")

    if enviar:
        try:
            if fila_index:
                col_index = df_ventas.columns.get_loc(mes.upper()) + 1
                ventas_sheet.update_cell(fila_index, col_index, cantidad)

            if "Carpeta privada" in user:
                match = re.search(r'/folders/([a-zA-Z0-9_-]+)', user["Carpeta privada"])
                carpeta_id = match.group(1) if match else None
                if carpeta_id:
                    service = conectar_drive(st.secrets["gcp_service_account"])
                    for archivo in fotos:
                        subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

            st.success("✅ Ventas enviadas correctamente.")
            time.sleep(2)
            st.session_state.widget_key_ventas = str(uuid.uuid4())
            st.session_state.widget_key_fotos = str(uuid.uuid4())
            st.rerun()
        except Exception as e:
            st.error(f"Error al subir ventas: {e}")

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
