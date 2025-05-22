import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from drive_upload import conectar_drive, subir_archivo_a_drive
from google_sheets import cargar_datos_hoja
from paginas.panel_punto import mostrar_panel

# CONFIGURA TU GOOGLE SHEET
SHEET_URL = "https://docs.google.com/spreadsheets/d/1a14wIe2893oS7zhicvT4mU0N_dM3vqItkTfJdHB325A"
PESTAÑA = "Registro"

@st.cache_data
def cargar_datos():
    return cargar_datos_hoja(SHEET_URL, pestaña=PESTAÑA)

st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")
st.image("https://lostmary-es.com/cdn/shop/files/logo_lostmary.png", width=150)
st.title("Área de Puntos de Venta")
st.write("Introduce tu correo para acceder a tu área personalizada:")

correo = st.text_input("Correo electrónico").strip().lower()

if correo:
    datos = cargar_datos()
    if correo in datos["Correo electrónico"].str.lower().values:
        punto = datos[datos["Correo electrónico"].str.lower() == correo].iloc[0]

        st.success(f"¡Bienvenido, {punto['Nombre del punto de venta']}!")

        mostrar_panel(punto, 0, [])

        # Inputs de promociones personalizadas
        promo1 = st.number_input("¿Cuántas promociones 2+1 TAPPO?", min_value=0, step=1)
        promo2 = st.number_input("¿Cuántas promociones 3×21 BM1000?", min_value=0, step=1)
        imagenes = st.file_uploader("Sube las fotos de los tickets o promociones", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        if st.button("Subir promociones"):
            if not imagenes:
                st.warning("Debes seleccionar al menos una imagen.")
            else:
                # Subir imágenes a carpeta de Drive
                service = conectar_drive(st.secrets["gcp_service_account"])
                carpeta_id = punto["Carpeta privada"]

                for imagen in imagenes:
                    subir_archivo_a_drive(service, imagen, imagen.name, carpeta_id)

                # Conectar a Sheets y actualizar columnas L, M, N
                SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
                service_account_info = st.secrets["gcp_service_account"]
                creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
                client = gspread.authorize(creds)
                sheet = client.open_by_url(SHEET_URL)
                worksheet = sheet.worksheet(PESTAÑA)

                correos = worksheet.col_values(3)
                fila_usuario = next((i + 1 for i, val in enumerate(correos) if val.strip().lower() == correo), None)

                if fila_usuario:
                    # Columna L = 12 → Promos 2+1 TAPPO
                    # Columna M = 13 → Promos 3×21 BM1000
                    # Columna N = 14 → Fecha

                    val1 = worksheet.cell(fila_usuario, 12).value
                    val2 = worksheet.cell(fila_usuario, 13).value

                    total1 = int(val1) if val1.isnumeric() else 0
                    total2 = int(val2) if val2.isnumeric() else 0

                    nuevo1 = total1 + promo1
                    nuevo2 = total2 + promo2

                    worksheet.update_cell(fila_usuario, 12, str(nuevo1))
                    worksheet.update_cell(fila_usuario, 13, str(nuevo2))
                    worksheet.update_cell(fila_usuario, 14, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    st.success(f"✅ Se subieron {len(imagenes)} imagen(es) y se actualizaron tus promociones.")
                    st.write(f"📦 Promociones 2+1 TAPPO acumuladas: {nuevo1}")
                    st.write(f"📦 Promociones 3×21 BM1000 acumuladas: {nuevo2}")
                else:
                    st.error("No se pudo localizar tu fila en el Excel.")
    else:
        st.error("Correo no encontrado. Asegúrate de que esté registrado en el formulario.")
