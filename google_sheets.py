import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def conectar_google_sheet(json_path, sheet_url):
    creds = Credentials.from_service_account_file(json_path, scopes=SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(sheet_url)
    return spreadsheet

def buscar_usuario_por_email(sheet, pestaña, email):
    worksheet = sheet.worksheet(pestaña)
    registros = worksheet.get_all_records()
    for fila in registros:
        if fila.get("Correo electrónico", "").strip().lower() == email.strip().lower():
            return fila
    return None

def cargar_datos_hoja(sheet_url, pestaña):
    creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_url(sheet_url)
    worksheet = spreadsheet.worksheet(pestaña)
    data = worksheet.get_all_records()
    import pandas as pd
    return pd.DataFrame(data)