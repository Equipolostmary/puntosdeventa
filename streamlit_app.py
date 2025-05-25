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

# Estilo
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, .block-container, .stApp, .main {
        background-color: #e6e0f8 !important;
        font-family: 'Montserrat', sans-serif;
    }
    section[data-testid="stSidebar"],
    #MainMenu,
    header,
    footer,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    div[data-testid="stActionButtonIcon"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión a Google Sheets
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

# VALIDACIÓN DE LOGIN
if "email" in st.session_state:
    correo_usuario = st.session_state["email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    with st.container():
        st.markdown(
            f"""
            <div style="background-color:#bda2e0;padding:15px 10px;text-align:center;
                        font-weight:bold;font-size:20px;color:black;border-radius:5px;">
                ÁREA PRIVADA – {nombre_usuario}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.image("logo.png", use_container_width=True)
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}! 🥳")
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
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(tapp
