from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def conectar_drive():
    scopes = ["https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service

def subir_archivo_a_carpeta(drive_service, folder_id, archivo_local, nombre_remoto):
    media = MediaFileUpload(archivo_local, resumable=True)
    file_metadata = {
        'name': nombre_remoto,
        'parents': [folder_id]
    }
    archivo_subido = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    return archivo_subido.get('id')
