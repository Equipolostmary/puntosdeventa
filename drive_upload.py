from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def conectar_drive(json_path):
    creds = Credentials.from_service_account_file(json_path, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)
    return service

def subir_archivo_a_drive(service, archivo, nombre_archivo, carpeta_id):
    file_metadata = {
        "name": nombre_archivo,
        "parents": [carpeta_id]
    }

    media = MediaIoBaseUpload(archivo, mimetype=archivo.type, resumable=True)
    archivo_subido = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    return archivo_subido.get("id")