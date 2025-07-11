from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from mimetypes import guess_type
import io
import streamlit as st
import json

# Conexión a Google Drive usando los secrets temporales
def conectar_drive():
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    # Usamos los secretos de la nueva cuenta de servicio temporal
    service_account_info = json.loads(st.secrets["google_service_account_temp"])

    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

# Subida genérica de archivo
def subir_archivo_a_drive(service, archivo, nombre_archivo, carpeta_id):
    mime_type = guess_type(nombre_archivo)[0] or "application/octet-stream"

    file_metadata = {
        "name": nombre_archivo,
        "parents": [carpeta_id]
    }

    media = MediaIoBaseUpload(archivo, mimetype=mime_type, resumable=False)

    archivo_subido = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return archivo_subido.get("id")

# Función directa para usar desde la app con archivo de Streamlit
def subir_archivo_a_drive_con_idcarpeta(file_streamlit, carpeta_id):
    service = conectar_drive()
    file_bytes = io.BytesIO(file_streamlit.read())
    file_bytes.seek(0)
    subir_archivo_a_drive(service, file_bytes, file_streamlit.name, carpeta_id)

# Crear carpeta nueva y guardar el enlace en Excel (columna L)
def crear_carpeta_y_guardar_en_excel(nombre_carpeta, id_padre, worksheet, fila_index):
    service = conectar_drive()

    # Crear la carpeta en Drive
    metadata = {
        "name": nombre_carpeta,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [id_padre]
    }
    carpeta = service.files().create(body=metadata, fields="id").execute()
    carpeta_id = carpeta["id"]
    enlace = f"https://drive.google.com/drive/folders/{carpeta_id}"

    # Guardar enlace en la columna L (columna 12)
    worksheet.update_cell(fila_index + 2, 12, enlace)  # +2 por cabecera

    return carpeta_id, enlace
