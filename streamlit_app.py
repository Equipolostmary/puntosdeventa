import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")

# Estilo visual
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

ADMIN_EMAIL = "equipolostmary@gmail.com"

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
if "email" in st.session_state:
    correo_usuario = st.session_state["email"]
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    nombre_usuario = user.get("Expendiduría", correo_usuario)

    st.markdown(f"<div style='background-color:#bda2e0;padding:15px 10px;text-align:center;"
                f"font-weight:bold;font-size:20px;color:black;border-radius:5px;'>"
                f"ÁREA PRIVADA – {nombre_usuario}</div>", unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {nombre_usuario}!")
    st.subheader("📋 Tus datos personales")

    columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
    for col in columnas_visibles:
        if "contraseña" not in col.lower():
            st.markdown(f"**{col}:** {user.get(col, '')}")

    # === PROMOCIONES ===
    st.markdown("---")
    st.header("🎁 Promociones")

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
    - 📅 **Última actualización:** {user.get('Ultima actualización', 'N/A')}
    """)

    st.subheader("📸 Subir nuevas promociones")
    promo1 = st.number_input("Promos 2+1 TAPPO", min_value=0, key="promo1")
    promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key="promo2")
    imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key="imgpromo")

    if st.button("Subir promociones"):
        if imagenes:
            service = conectar_drive(st.secrets["gcp_service_account"])
            carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
            for img in imagenes:
                subir_archivo_a_drive(service, img, img.name, carpeta_id)
            row = user.name + 2
            worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(tappo_asig + promo1))
            worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(bm_asig + promo2))
            col_actualizacion = [c for c in df.columns if "actualiz" in c.lower()][0]
            worksheet.update_cell(row, df.columns.get_loc(col_actualizacion)+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.success("✅ Imágenes subidas y contadores actualizados correctamente.")
            st.experimental_rerun()
        else:
            st.warning("Selecciona al menos una imagen.")
    # === INCENTIVO VENTAS ===
    st.markdown("---")
    st.header("💰 Incentivo compensaciones mensuales")

    ventas_sheet = client.open("Compensaciones Mensuales").worksheet("General")
    valores = ventas_sheet.get_all_values()
    df_ventas = pd.DataFrame(valores[1:], columns=valores[0])
    df_ventas["TELÉFONO"] = df_ventas["TELÉFONO"].astype(str).str.strip()

    telefono_usuario = str(user.get("Teléfono")).strip()
    fila_usuario = df_ventas[df_ventas["TELÉFONO"] == telefono_usuario]

    ventas_marzo = ventas_abril = ventas_mayo = ventas_junio = "No disponible"
    incentivo_texto = "No asignado"
    fila_index = None

    if not fila_usuario.empty:
        fila_index = fila_usuario.index[0] + 2
        ventas_marzo = fila_usuario["MARZO"].values[0]
        ventas_abril = fila_usuario["ABRIL"].values[0]
        ventas_mayo = fila_usuario["MAYO"].values[0]
        ventas_junio = fila_usuario["JUNIO"].values[0]
        if "OBJETIVOS Y COMPENSACIONES" in fila_usuario.columns:
            incentivo_texto = fila_usuario["OBJETIVOS Y COMPENSACIONES"].values[0]
        elif "OBJETIVO" in fila_usuario.columns:
            incentivo_texto = fila_usuario["OBJETIVO"].values[0]

    st.markdown(f"**🎯 Objetivo asignado:** {incentivo_texto}")
    st.markdown(f"**📊 Marzo:** {ventas_marzo}")
    st.markdown(f"**📊 Abril:** {ventas_abril}")
    st.markdown(f"**📊 Mayo:** {ventas_mayo}")
    st.markdown(f"**📊 Junio:** {ventas_junio}")

    st.subheader("📤 Reporta tus ventas del mes")

    with st.form("formulario_ventas"):
        mes = st.selectbox("Selecciona el mes", ["Mayo", "Junio"])
        cantidad = st.number_input(f"¿Cuántos dispositivos has vendido en {mes.lower()}?", min_value=0, step=1, key="venta")
        fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True, key="imgventas")
        enviar = st.form_submit_button("Enviar")

    if enviar:
        if fila_index:
            col = 15 if mes == "Mayo" else 16
            ventas_sheet.update_cell(fila_index, col, cantidad)

        if "Carpeta privada" in user:
            match = re.search(r'/folders/([a-zA-Z0-9_-]+)', user["Carpeta privada"])
            carpeta_id = match.group(1) if match else None
            if carpeta_id:
                service = conectar_drive(st.secrets["gcp_service_account"])
                for archivo in fotos:
                    subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

        st.success("✅ Ventas enviadas correctamente.")
        st.experimental_rerun()

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
                st.session_state["email"] = correo
                st.rerun()
