import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import os
from drive_upload import conectar_drive, subir_archivo_a_carpeta

st.set_page_config(page_title="Promoción 3x13", layout="centered")
st.markdown("<h2 style='text-align: center;'>Subida promoción 3x13 TAPPO</h2>", unsafe_allow_html=True)

# Conexión a Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes
)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

# Login de usuario
st.markdown("**Inicio de sesión**")
usuario = st.text_input("Usuario")
clave = st.text_input("Contraseña", type="password")

if st.button("Entrar"):
    if usuario in df["Usuario"].values:
        fila_usuario = df[df["Usuario"] == usuario].index[0]
        if str(df.loc[fila_usuario, "Contraseña"]) == clave:
            st.success("Bienvenido, " + usuario)
            carpeta_drive = df.loc[fila_usuario, "CARPETA"]
            contador_actual = df.loc[fila_usuario, "Promos 3x13 TAPPO"] if "Promos 3x13 TAPPO" in df.columns else 0

            st.markdown("<hr>", unsafe_allow_html=True)
            st.subheader("Registrar nueva promo 3x13")

            cantidad = st.number_input("Cantidad de promociones realizadas", min_value=1, step=1)
            foto = st.file_uploader("Sube una foto del ticket", type=["jpg", "jpeg", "png"])

            if st.button("Enviar"):
                if foto is not None:
                    drive_service = conectar_drive()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"promo3x13_{usuario}_{timestamp}.jpg"

                    with open(nombre_archivo, "wb") as f:
                        f.write(foto.read())

                    subir_archivo_a_carpeta(drive_service, nombre_archivo, carpeta_drive)
                    os.remove(nombre_archivo)

                    nuevo_total = int(contador_actual) + int(cantidad)
                    df.at[fila_usuario, "Promos 3x13 TAPPO"] = nuevo_total
                    worksheet.update_cell(fila_usuario + 2, df.columns.get_loc("Promos 3x13 TAPPO") + 1, nuevo_total)

                    st.success("¡Promoción registrada correctamente!")
                else:
                    st.error("Por favor, sube una foto del ticket.")
        else:
            st.error("Contraseña incorrecta")
    else:
        st.error("Usuario no encontrado")
