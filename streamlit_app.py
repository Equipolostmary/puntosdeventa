# === INICIO ===
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

# === ENLACES ===
enlaces = {
    "ACCIONES COMERCIALES Q4 2024": "https://docs.google.com/spreadsheets/d/1DqC1348Z3LqnzCVB8d8AqDbsAR3WUDUf/edit?gid=1142706501#gid=1142706501",
    "CATALOGO DE MATERIALES": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-YPxpn22EL6g/p/10ciZH8DpEsC5GNpYSigFrFJ_Fln9B0Q2/preview?authuser=0",
    "COMPENSACIONES MENSUALES": "https://docs.google.com/spreadsheets/d/1CpHwmPrRYqqMtXrZBZV7-nQ0eEH6Z-RWtpnT84ZtVB0/edit?gid=128791843#gid=128791843",
    "CORREO ELECTRONICO": "https://email.ionos.es/appsuite/#!&app=io.ox/mail&folder=default0/INBOX",
    "EVENTOS": "https://docs.google.com/spreadsheets/d/1VTzXhfGb0d1kiuN4HuHrcotvy0HzOENCjLkeaV3FNA/edit?gid=0#gid=0",
    "EXCELL VACACIONES": "https://ideasoriginales4-my.sharepoint.com/:x:/r/personal/erselfbar_ioinvestigacion_com/Documents/PROYECTO%20LOST%20MERY%20-%20ELFBAR/1.%20VACACIONES%202025/Vacaciones%20Equipo%20Lost%20Mary%202025.xlsx",
    "EXPENDIDURÍAS": "https://serviciostelematicosext.hacienda.gob.es/CMT/GestitabExt/Egeo/index.cshtml",
    "FOTOS COMPENSACIONES": "https://drive.google.com/drive/u/1/folders/18SxC9Wy9VTz-W2auyIBMwaVU6yRqsHXA",
    "FOTOS DE LOS TICKET": "https://drive.google.com/drive/u/1/folders/1GpG-NERdKzZVItqa5v7B88BW_UAmb_e4",
    "PERSONIO": "https://login.personio.com/login",
    "PRECIO BM600": "https://docs.google.com/spreadsheets/d/1F-TyJSI32sIBvZtXUkfFQ5P2rQQeXHNISx1u95vi4o/edit?gid=0#gid=0",
    "REALIZAR PEDIDO": "https://docs.google.com/spreadsheets/d/1IUeYNQg3Dx4NK45K6vrikRWNq3vkM8HXplH8Ymb8h3tI/edit?gid=2078407623#gid=2078407623",
    "REGISTRAR PUNTO DE VENTA": "https://docs.google.com/forms/d/e/1FAIpQLScTNcjTq0DU2xIjB1EcqbVpcVXWlKurBiNBZFDngN3fhmYb1_A/viewform",
    "RESPUESTAS FORMULARIOS": "https://drive.google.com/drive/folders/1eNhwJQBf6ZqkR2X76MQdEy3-Fj1WfVQX",
    "VIDEOS": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-YPxpn22EL6g/p/1hzXetHR3hVMwCE-Z7A0GGsMmI7q3hqjT/preview?authuser=0",
    "VINILOS": "https://docs.google.com/spreadsheets/d/112hSu3vSu0wBMCvAuMGFsANoAV7v2vfskI0Xm4ArX3Oc/edit?gid=0#gid=0",
    "VISUALES": "https://drive.google.com/drive/folders/1qzXCVrBcAuebu2kpen9sQ8X85ZIDh68C",
    "WEB DE ESTANCOS": "https://sites.google.com/view/estancoslostmary",
    "INTRODUCCION TAPPO": "https://drive.google.com/drive/u/1/folders/18KFVvu3Fg3W_Gr5erYtAXiPPG3zAxg8L"
}

# (continúa...)
# === AUTENTICACIÓN Y DATOS ===
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())
df.columns = df.columns.str.strip()

# === DEFINICIÓN DE COLUMNAS DE PROMOCIONES ===
promo_tappo_col = "Promoción 3x13 TAPPO"
promo_bm1000_col = "Promoción 3×21 BM1000"
promo_tappo_2x1_col = "2+1 TAPPO"
total_promos_col = "TOTAL PROMOS"

# === VERIFICACIÓN DE COLUMNAS CLAVE ===
columnas_necesarias = [promo_tappo_col, promo_bm1000_col, promo_tappo_2x1_col, total_promos_col]
for col in columnas_necesarias:
    if col not in df.columns:
        st.error(f"La columna '{col}' no se encuentra en el Excel. Verifica los nombres exactos.")
        st.stop()

# === FUNCIÓN PARA BUSCAR USUARIO POR CORREO ===
def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# === INICIO DE SESIÓN ===
if "auth_email" not in st.session_state:
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
# === ÁREA PRIVADA ===
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")
    if st.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    st.markdown("### Estado de promociones")
    def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
    tappo = val(promo_tappo_col)
    bm1000 = val(promo_bm1000_col)
    tappo_2x1 = val(promo_tappo_2x1_col)
    total = tappo + bm1000 + tappo_2x1

    st.write(f"- Promos 3x13 TAPPO: {tappo}")
    st.write(f"- Promos BM1000: {bm1000}")
    st.write(f"- Promos 2+1 TAPPO: {tappo_2x1}")
    st.write(f"- Total promociones acumuladas: {total}")

    st.markdown("### Subir nuevas promociones")
    if "widget_key_promos" not in st.session_state:
        st.session_state.widget_key_promos = str(uuid.uuid4())
    if "widget_key_imgs" not in st.session_state:
        st.session_state.widget_key_imgs = str(uuid.uuid4())

    promo1 = st.number_input("Promos 3x13 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
    promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
    promo3 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_3")
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
                row = df[df["Usuario"] == user["Usuario"]].index[0] + 2
                worksheet.update_cell(row, df.columns.get_loc(promo_tappo_col)+1, str(tappo + promo1))
                worksheet.update_cell(row, df.columns.get_loc(promo_bm1000_col)+1, str(bm1000 + promo2))
                worksheet.update_cell(row, df.columns.get_loc(promo_tappo_2x1_col)+1, str(tappo_2x1 + promo3))
                nuevo_total = tappo + promo1 + bm1000 + promo2 + tappo_2x1 + promo3
                worksheet.update_cell(row, df.columns.get_loc(total_promos_col)+1, str(nuevo_total))
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.success("✅ Imágenes subidas correctamente. Contadores actualizados.")
                time.sleep(2)
                st.rerun()
    st.markdown("### Incentivo compensaciones mensuales")
    objetivo = user.get("OBJETIVO", "")
    compensacion = user.get("COMPENSACION", "")
    ventas_mensuales = user.get("VENTAS MENSUALES", "")

    st.write(f"- OBJETIVO: {objetivo if objetivo else '*No asignado*'}")
    st.write(f"- COMPENSACIÓN: {compensacion if compensacion else '*No definido*'}")
    st.write(f"- Ventas acumuladas: {ventas_mensuales if ventas_mensuales else '*Sin registrar*'}")

    st.markdown("### Reporta tus ventas")
    if "widget_key_ventas" not in st.session_state:
        st.session_state.widget_key_ventas = str(uuid.uuid4())
    if "widget_key_fotos" not in st.session_state:
        st.session_state.widget_key_fotos = str(uuid.uuid4())

    with st.form("formulario_ventas"):
        cantidad = st.number_input("¿Cuántos dispositivos has vendido este mes?", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
        fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
        enviar = st.form_submit_button("Enviar")

    if enviar:
        if not fotos:
            st.warning("Debes subir al menos una imagen.")
        else:
            try:
                col_destino = "VENTAS MENSUALES"
                row = df[df["Usuario"] == user["Usuario"]].index[0] + 2
                col_index = df.columns.get_loc(col_destino) + 1
                valor_anterior = user.get(col_destino, 0)
                anterior = int(valor_anterior) if str(valor_anterior).isdigit() else 0
                suma = anterior + int(cantidad)
                worksheet.update_cell(row, col_index, str(suma))

                match = re.search(r'/folders/([a-zA-Z0-9_-]+)', user["Carpeta privada"])
                carpeta_id = match.group(1) if match else None
                if carpeta_id:
                    service = conectar_drive(st.secrets["gcp_service_account"])
                    for archivo in fotos:
                        subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

                st.success("Ventas enviadas correctamente.")
                time.sleep(2)
                st.session_state.widget_key_ventas = str(uuid.uuid4())
                st.session_state.widget_key_fotos = str(uuid.uuid4())
                st.rerun()
            except Exception as e:
                st.error(f"Error al subir ventas: {e}")
else:
    # Si no hay sesión iniciada, se muestra la pantalla de login (esto ya está arriba)
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
