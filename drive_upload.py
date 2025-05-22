from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from mimetypes import guess_type

# Conexión a Google Drive usando las credenciales de Streamlit Secrets
def conectar_drive(secret_dict):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(secret_dict, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

# Subida de archivo a una carpeta específica
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
