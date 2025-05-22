import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
import gspread
from drive_upload import conectar_drive, subir_archivo_a_drive  # ← si ya los tienes
from google_sheets import cargar_datos_hoja                     # ← si ya lo tienes

# --- CONFIGURACIÓN BÁSICA Y ESTILO ---
st.set_page_config(page_title="Lost Mary – Área de Puntos", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(135deg,#e3aeea,#caa7ff);
}
html,body,[class*="css"]{font-family:'Montserrat',sans-serif;}
h1,h2,h3,h4{font-weight:700;color:#1b0032;}
.stTextInput > div > div > input{
    border:2px solid #6a0dad;background:#fff;color:#000;
    font-weight:600;box-shadow:0 0 6px rgba(0,0,0,.2);
}
.stButton > button{
    background:#6a0dad;color:#fff;font-weight:700;
    border-radius:6px;padding:8px 20px;font-size:16px;
}
#MainMenu,header,footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS DESDE GOOGLE SHEETS ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["sheet_id"])       # ID de tu sheet en secrets
worksheet = sheet.worksheet("Registro")                  # pestaña 'Registro'
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Función auxiliar para encontrar al usuario
def get_user_row(email: str):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# Logo centrado
st.image("logo.png", use_container_width=True)

# --- LOGIN (correo + contraseña) ---
st.title("Iniciar sesión")
email_input = st.text_input("Correo electrónico").strip().lower()
password_input = st.text_input("Contraseña", type="password")
login_btn = st.button("Acceder")

if login_btn:
    if not email_input or not password_input:
        st.warning("Por favor, rellena ambos campos.")
    else:
        user_row = get_user_row(email_input)
        if user_row is None:
            st.error("Correo no encontrado.")
        elif str(user_row.get("Contraseña", "")).strip() != password_input:
            st.error("Contraseña incorrecta.")
        else:
            st.session_state.auth_email = email_input
            st.experimental_rerun()

# --- PANEL PRIVADO ---
if "auth_email" in st.session_state:
    user_email = st.session_state.auth_email
    user_row = get_user_row(user_email)

    if user_row is None:
        st.error("Hubo un problema: usuario no encontrado.")
        st.session_state.pop("auth_email")
        st.stop()

    # Saludo personalizado
    st.success(f"¡Bienvenido, {user_row['Expendiduría']}!")
    st.subheader("📋 Información del punto de venta")

    # Mostrar datos excepto contraseña y correo
    for col, val in user_row.items():
        if str(col).lower() in {"contraseña", "contrasena", "password",
                                "correo", "correo electrónico", "email",
                                "dirección de correo electrónico"}:
            continue
        st.markdown(f"**{col}:** {val}")

    # --- CONTADORES DE PROMOCIONES ---
    total_tappo = user_row.get("Promoción 2+1 TAPPO", 0)
    total_bm    = user_row.get("Promoción 3×21 BM1000", 0)
    entreg_tappo = user_row.get("ENTREGADOS PROMO TAPPO", 0)
    entreg_bm    = user_row.get("ENTREGADOS PROMO BM1000", 0)
    falta_tappo  = user_row.get("FALTA POR ENTREGAR TAPPO", 0)
    falta_bm     = user_row.get("FALTA POR ENTREGAR BM1000", 0)

    st.subheader("📦 Estado de tus promociones")
    st.markdown(f"- **TAPPO asignados:** {total_tappo}")
    st.markdown(f"- **TAPPO entregados:** {entreg_tappo}")
    st.markdown(f"- **TAPPO por entregar:** {falta_tappo}")
    st.markdown(f"- **BM1000 asignados:** {total_bm}")
    st.markdown(f"- **BM1000 entregados:** {entreg_bm}")
    st.markdown(f"- **BM1000 por entregar:** {falta_bm}")

    # --- SUBIDA DE NUEVAS PROMOCIONES (si usas Drive) ---
    st.subheader("📸 Subir nuevas promociones")
    promo1 = st.number_input("¿Cuántas promociones 2+1 TAPPO quieres registrar?", min_value=0, step=1)
    promo2 = st.number_input("¿Cuántas promociones 3×21 BM1000 quieres registrar?", min_value=0, step=1)
    imagenes = st.file_uploader(
        "Sube las fotos de los tickets o promociones",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )
    if st.button("Subir promociones"):
        if not imagenes:
            st.warning("Selecciona al menos una imagen.")
        else:
            service = conectar_drive(st.secrets["gcp_service_account"])
            carpeta_id = str(user_row["Carpeta privada"]).split("/")[-1]
            success = 0
            for img in imagenes:
                try:
                    subir_archivo_a_drive(service, img, img.name, carpeta_id)
                    success += 1
                except Exception as e:
                    st.error(f"No se pudo subir {img.name}: {e}")
            if success:
                row_idx = user_row.name + 2  # +2 por encabezado + 0-index
                new_tappo = int(total_tappo) + promo1
                new_bm    = int(total_bm) + promo2
                worksheet.update_cell(row_idx, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(new_tappo))
                worksheet.update_cell(row_idx, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(new_bm))
                worksheet.update_cell(row_idx, df.columns.get_loc("Última actualización")+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.success(f"Subidas {success} imágenes y actualizados tus contadores.")

    # --- VISTA DEL ADMIN ---
    if user_email == ADMIN_EMAIL:
        st.subheader("📊 Resumen de promociones por punto de venta")
        # Copia del dataframe con columnas seleccionadas
        cols_mostrar = ["Expendiduría", "Dirección de correo electrónico",
                        "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
                        "ENTREGADOS PROMO TAPPO", "ENTREGADOS PROMO BM1000",
                        "FALTA POR ENTREGAR TAPPO", "FALTA POR ENTREGAR BM1000",
                        "Última actualización"]
        df_admin = df[cols_mostrar].fillna(0)
        st.dataframe(df_admin, use_container_width=True)
