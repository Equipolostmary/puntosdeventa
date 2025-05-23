# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid

st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")

ADMIN_EMAIL = "equipolostmary@gmail.com"

# Estilo visual y ocultar menús
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, .block-container, .stApp, .main {
        background-color: #e6e0f8 !important;
        font-family: 'Montserrat', sans-serif;
    }
    section[data-testid="stSidebar"], #MainMenu, header, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión con Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

def buscar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

def obtener_urls_imagenes(creds, folder_id):
    drive = build('drive', 'v3', credentials=creds)
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive.files().list(q=query, fields="files(id, name, webContentLink, mimeType)").execute()
    return [file.get("webContentLink") for file in results.get("files", []) if "image" in file.get("mimeType", "")]

if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

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
    - 🕓 **Última actualización:** {user.get('Ultima actualización', 'N/A')}
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
            carpeta_url = str(user["Carpeta privada"])
            carpeta_id = carpeta_url.split("/folders/")[-1].split("?")[0]
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
                worksheet.update_cell(row, df.columns.get_loc("Ultima actualización")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state["subida_ok"] = True
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.rerun()

    # 🏛️ Galería de imágenes
    st.subheader("🏬 Galería de imágenes")
    if correo_usuario == ADMIN_EMAIL:
        usuarios = df["Expendiduría"].tolist()
        seleccionado = st.selectbox("Seleccionar usuario", usuarios)
        user_sel = df[df["Expendiduría"] == seleccionado].iloc[0]
    else:
        user_sel = user

    carpeta_id_sel = str(user_sel["Carpeta privada"]).split("/folders/")[-1].split("?")[0]
    try:
        imagenes_urls = obtener_urls_imagenes(creds, carpeta_id_sel)
        cols = st.columns(3)
        for i, img_url in enumerate(imagenes_urls):
            cols[i % 3].image(img_url)
    except Exception as e:
        st.warning(f"No se pudieron cargar imágenes: {e}")

    # Vista completa solo para el maestro
    if correo_usuario == ADMIN_EMAIL:
        st.subheader("📊 Vista completa de todos los puntos")
        columnas = [
            "Expendiduría", "Dirección de correo electrónico", "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "Entregados promo TAPPO", "Entregados promo BM1000",
            "Falta por entregar TAPPO", "Falta por entregar BM1000",
            "Ultima actualización"
        ]
        st.dataframe(df[columnas].fillna(0), use_container_width=True)

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
