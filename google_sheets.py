import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

def cargar_datos_hoja(sheet_url, pestaña):
    SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    worksheet = sheet.worksheet(pestaña)
    datos = worksheet.get_all_records()
    return pd.DataFrame(datos)
