from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from mimetypes import guess_type
import io
import streamlit as st

# Conectar con Google Drive usando secrets de Streamlit
def conectar_drive(secret_dict):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(secret_dict, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

# Subir archivo a Drive en una carpeta concreta
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

# Función preparada para subir desde Streamlit a carpeta privada
def subir_archivo_a_drive_con_idcarpeta(file_streamlit, carpeta_id):
    service = conectar_drive(st.secrets["gcp_service_account"])

    # Convertir archivo a bytes
    file_bytes = io.BytesIO(file_streamlit.read())
    file_bytes.seek(0)

    subir_archivo_a_drive(service, file_bytes, file_streamlit.name, carpeta_id)
