import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive

# CONFIG
st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ESTILO
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(135deg, #d5a7ff, #f3d6ff);
}
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}
.stTextInput input, .stButton > button {
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# CONEXIÓN GOOGLE SHEETS
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

# FUNCIONES
def buscar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# LOGO
st.image("logo.png", use_container_width=True)

# CERRAR SESIÓN
if "auth_email" in st.session_state and st.button("Cerrar sesión"):
    st.session_state.clear()
    st.experimental_rerun()

# LOGIN
if "auth_email" not in st.session_state:
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder") or st.session_state.get("trigger_login"):
        st.session_state["trigger_login"] = False
        if not correo or not clave:
            st.warning("Debes completar ambos campos.")
        else:
            user = buscar_usuario(correo)
            if user is None:
                st.error("Correo no encontrado.")
            else:
                pwd = str(user.get("Contraseña", "")).strip().replace(",", "")
                entrada = clave.strip().replace(",", "")
                if not pwd:
                    st.error("No hay contraseña configurada.")
                elif pwd != entrada:
                    st.error("Contraseña incorrecta.")
                else:
                    st.session_state.auth_email = correo
                    st.success("Iniciando sesión...")
                    st.stop()

# PANEL PRIVADO
if "auth_email" in st.session_state:
    correo_usuario = st.session_state.auth_email
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.stop()

    st.markdown(f"### 👤 Bienvenido, **{user['Expendiduría']}**")
    st.markdown("---")
    st.markdown("### 📦 Estado de promociones")

    def valor(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0

    promo_tappo = valor("Promoción 2+1 TAPPO")
    promo_bm = valor("Promoción 3×21 BM1000")
    entregado_tappo = valor("ENTREGADOS PROMO TAPPO")
    entregado_bm = valor("ENTREGADOS PROMO BM1000")
    falta_tappo = valor("FALTA POR ENTREGAR TAPPO")
    falta_bm = valor("FALTA POR ENTREGAR BM1000")

    st.markdown(f"""
    - **🟣 Promoción TAPPO asignados:** {promo_tappo}
    - ✅ **Entregados TAPPO:** {entregado_tappo}
    - ⏳ **Pendientes TAPPO:** {falta_tappo}

    - **🟣 Promoción BM1000 asignados:** {promo_bm}
    - ✅ **Entregados BM1000:** {entregado_bm}
    - ⏳ **Pendientes BM1000:** {falta_bm}

    - 🕓 **Última actualización:** {user.get("Última actualización", "N/A")}
    """)

    st.markdown("### 📸 Subir nuevas promociones")
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
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(promo1 + promo_tappo))
                worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(promo2 + promo_bm))
                worksheet.update_cell(row, df.columns.get_loc("Última actualización")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.success(f"✅ {ok} imagen(es) subidas. Contadores actualizados.")
                st.experimental_rerun()

# VISTA COMPLETA PARA EL ADMINISTRADOR
    if correo_usuario == ADMIN_EMAIL:
        st.markdown("### 📊 Vista completa de todos los puntos")
        columnas = [
            "Expendiduría", "Dirección de correo electrónico",
            "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "ENTREGADOS PROMO TAPPO", "ENTREGADOS PROMO BM1000",
            "FALTA POR ENTREGAR TAPPO", "FALTA POR ENTREGAR BM1000",
            "Última actualización"
        ]
        try:
            st.dataframe(df[columnas].fillna(0), use_container_width=True)
        except KeyError as e:
            st.error(f"⚠️ Faltan columnas esperadas en el Excel: {e}")
