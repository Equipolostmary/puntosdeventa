import streamlit as st
import pandas as pd
from datetime import datetime
from google.oauth2 import service_account
import gspread
from drive_upload import subir_archivo_a_drive_con_idcarpeta
import re

# Cargar credenciales de servicio
creds = service_account.Credentials.from_service_account_file(
    'credenciales.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
)
client = gspread.authorize(creds)

# Abrir hojas de Google Sheets
registro_sheet = client.open("Registro promociones Lostmary").worksheet("Registro")
ventas_sheet = client.open("Compensaciones Mensuales").worksheet("General")

# Cargar datos como DataFrames
df_registro = pd.DataFrame(registro_sheet.get_all_records())
df_ventas = pd.DataFrame(ventas_sheet.get_all_records())

# Obtener email del usuario logueado
email_usuario = st.session_state.get("email")
registro_fila = df_registro[df_registro["Correo"] == email_usuario]

if not registro_fila.empty:
    telefono_usuario = registro_fila["Teléfono"].values[0]
    enlace_carpeta = registro_fila["Carpeta privada"].values[0] if "Carpeta privada" in registro_fila.columns else ""

    # Extraer ID de carpeta de Google Drive si existe
    carpeta_id = None
    if isinstance(enlace_carpeta, str) and "/folders/" in enlace_carpeta:
        match = re.search(r'/folders/([a-zA-Z0-9_-]+)', enlace_carpeta)
        carpeta_id = match.group(1) if match else None

    # Buscar fila correspondiente en Excel de ventas
    fila_usuario = df_ventas[df_ventas["F"] == telefono_usuario]

    # Inicializar variables por si no encuentra datos
    ventas_marzo = ventas_abril = ventas_mayo = ventas_junio = "No disponible aún"
    fila_index = None

    if not fila_usuario.empty:
        fila_index = fila_usuario.index[0] + 2  # +2 por encabezado
        ventas_marzo = fila_usuario["M"].values[0]
        ventas_abril = fila_usuario["N"].values[0]
        ventas_mayo = fila_usuario["O"].values[0]
        ventas_junio = fila_usuario["P"].values[0]

    # Mostrar historial de ventas
    st.subheader("📊 Historial de Ventas")
    st.markdown(f"**Marzo:** {ventas_marzo}")
    st.markdown(f"**Abril:** {ventas_abril}")
    st.markdown(f"**Mayo:** {ventas_mayo}")
    st.markdown(f"**Junio:** {ventas_junio}")

    st.divider()
    st.subheader("📤 Reporta tus ventas del mes")

    with st.form("formulario_ventas"):
        input_mayo = st.number_input("¿Cuántos dispositivos Lost Mary has vendido en mayo?", min_value=0, step=1)
        input_junio = st.number_input("¿Cuántos dispositivos Elfbar has vendido en junio?", min_value=0, step=1)
        fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True)
        enviar = st.form_submit_button("Enviar")

    if enviar:
        if fila_index:
            ventas_sheet.update_cell(fila_index, 15, input_mayo)   # Columna O
            ventas_sheet.update_cell(fila_index, 16, input_junio)  # Columna P

        if carpeta_id:
            for archivo in fotos:
                subir_archivo_a_drive_con_idcarpeta(archivo, carpeta_id)

        st.success("✅ Datos enviados correctamente")

else:
    st.warning("Tu correo no está registrado en la base.")
