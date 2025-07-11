import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered", initial_sidebar_state="collapsed")

# ============ AUTENTICACIÓN ============
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())
df.columns = df.columns.str.strip()

# ============ CREAR CARPETAS PRIVADAS SI FALTAN ============
ID_CARPETA_RAIZ = "1YgVIv7j_u38UuDpWnDzgGiqAvxpE-XXc"
service = conectar_drive()
for idx, row in df.iterrows():
    enlace_actual = str(row.get("Carpeta privada", "")).strip()
    if not enlace_actual.startswith("https://drive.google.com/drive/folders/"):
        nombre_carpeta = f"{row.get('Expendiduría', 'Punto')} - {row.get('Usuario', 'SinUsuario')}"
        try:
            metadata = {
                "name": nombre_carpeta,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [ID_CARPETA_RAIZ]
            }
            carpeta = service.files().create(body=metadata, fields="id").execute()
            carpeta_id = carpeta.get("id")
            enlace = f"https://drive.google.com/drive/folders/{carpeta_id}"
            time.sleep(1)
            worksheet.update_cell(idx + 2, df.columns.get_loc("Carpeta privada") + 1, enlace)
            df.at[idx, "Carpeta privada"] = enlace
        except Exception as e:
            st.warning(f"No se pudo crear carpeta para {nombre_carpeta}: {e}")

# ============ BUSCAR USUARIO ============
def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

def to_float(value):
    try:
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

# ============ LOGIN ============
if "auth_email" not in st.session_state:
    st.image("logo.png", use_container_width=True)
    st.markdown("## Iniciar sesión")
    with st.form("login"):
        correo = st.text_input("Usuario").strip().lower()
        clave = st.text_input("Contraseña", type="password")
        acceder = st.form_submit_button("ACCEDER")
    if acceder:
        user = buscar_usuario(correo)
        if user is None:
            st.error("❌ Usuario no encontrado.")
        elif str(user.get("Contraseña", "")) != clave:
            st.error("❌ Contraseña incorrecta.")
        else:
            st.session_state["auth_email"] = correo
            st.rerun()

# ============ ÁREA PRIVADA USUARIO ============
else:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.image("logo.png", use_container_width=True)
    st.markdown(f"## Bienvenido, {user.get('Expendiduría', correo_usuario)}")

    # Mostrar datos básicos
    st.markdown("#### Mis datos")
    columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
    for col in columnas_visibles:
        if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
            st.markdown(f"**{col}:** {user.get(col, '')}")

    if user.get("Carpeta privada"):
        st.markdown(f"[📂 Abrir carpeta privada]({user['Carpeta privada']})")

    # ===== PROMOCIONES =====
    promo_col = "Promoción 3x13"
    total = int(to_float(user.get(promo_col, 0)))
    st.markdown(f"#### Promociones 3x13 acumuladas: **{total}**")

    with st.expander("Subir nuevas promociones"):
        cantidad = st.number_input("¿Cuántas promociones 3x13?", min_value=0)
        fotos = st.file_uploader("Sube fotos del ticket", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        if st.button("Subir promociones"):
            if not fotos:
                st.warning("⚠️ Debes subir al menos una imagen como comprobante.")
            else:
                try:
                    carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
                    for archivo in fotos:
                        subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)
                    fila = df[df["Usuario"] == user["Usuario"]].index[0] + 2
                    col_idx = df.columns.get_loc(promo_col) + 1
                    worksheet.update_cell(fila, col_idx, str(total + cantidad))
                    st.success("✅ Promociones subidas y contadas correctamente.")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al subir promociones: {e}")

    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
