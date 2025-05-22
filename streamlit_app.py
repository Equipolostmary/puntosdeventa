        st.dataframe(df[cols].fillna(0), use_container_width=True)import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive

st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# Estilo visual
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(135deg, #e3aeea, #caa7ff);
}
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}
.stTextInput input, .stButton > button {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Conexión a Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

def buscar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# Logo
st.image("logo.png", use_container_width=True)

# Botón cerrar sesión
if "auth_email" in st.session_state and st.button("Cerrar sesión"):
    del st.session_state.auth_email
    st.experimental_rerun()

# Login
if "auth_email" not in st.session_state:
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        if not correo or not clave:
            st.warning("Completa ambos campos.")
        else:
            user = buscar_usuario(correo)
            if user is None:
                st.error("Correo no encontrado.")
            elif str(user.get("Contraseña", "")).strip() != clave:
                st.error("Contraseña incorrecta.")
            else:
                st.session_state.auth_email = correo
                st.experimental_rerun()

# Panel privado
if "auth_email" in st.session_state:
    correo_usuario = st.session_state.auth_email
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        del st.session_state.auth_email
        st.stop()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")
    st.subheader("📋 Tus datos")

    for col, val in user.items():
        if str(col).lower() not in ["contraseña", "correo", "correo electrónico", "dirección de correo electrónico"]:
            st.markdown(f"**{col}:** {val}")

    # Promociones
    st.subheader("📦 Estado de promociones")
    campos = {
        "Promoción 2+1 TAPPO": "🟣 TAPPO asignados",
        "ENTREGADOS PROMO TAPPO": "✅ TAPPO entregados",
        "FALTA POR ENTREGAR TAPPO": "⏳ TAPPO por entregar",
        "Promoción 3×21 BM1000": "🟣 BM1000 asignados",
        "ENTREGADOS PROMO BM1000": "✅ BM1000 entregados",
        "FALTA POR ENTREGAR BM1000": "⏳ BM1000 por entregar"
    }
    for key, label in campos.items():
        if key in user:
            st.markdown(f"**{label}:** {user[key]}")

    # Subida de imágenes
    st.subheader("📸 Subir nuevas promociones")
    promo1 = st.number_input("Promos 2+1 TAPPO", min_value=0)
    promo2 = st.number_input("Promos 3×21 BM1000", min_value=0)
    imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png"], accept_multiple_files=True)

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
                t1 = int(user.get("Promoción 2+1 TAPPO", 0)) + promo1
                t2 = int(user.get("Promoción 3×21 BM1000", 0)) + promo2
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(t1))
                worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(t2))
                worksheet.update_cell(row, df.columns.get_loc("Última actualización")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.success(f"Se subieron {ok} imagen(es) y se actualizaron los contadores.")

    # Vista admin
    if correo_usuario == ADMIN_EMAIL:
        st.subheader("📊 Vista completa de todos los puntos")
        cols = [
            "Expendiduría", "Dirección de correo electrónico",
            "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "ENTREGADOS PROMO TAPPO", "ENTREGADOS PROMO BM1000",
            "FALTA POR ENTREGAR TAPPO", "FALTA POR ENTREGAR BM1000",
            "Última actualización"
        ]
        st.dataframe(df[cols].fillna(0), use_container_width=True)
