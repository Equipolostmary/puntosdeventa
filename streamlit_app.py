import streamlit as st
import pandas as pd
from google_sheets import cargar_datos_hoja
from drive_upload import conectar_drive, subir_archivo_a_drive
from paginas.panel_punto import mostrar_panel

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

        promociones = st.number_input("¿Cuántas promociones vas a subir?", min_value=1, step=1)
        imagenes = st.file_uploader("Sube las fotos de los tickets o promociones", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

        mostrar_panel(punto, promociones, imagenes)

        if st.button("Subir promociones"):
            if not imagenes:
                st.warning("Debes seleccionar al menos una imagen.")
            else:
                service = conectar_drive("service_account.json")
                carpeta_id = punto["Carpeta Drive"]
                for imagen in imagenes:
                    subir_archivo_a_drive(service, imagen, imagen.name, carpeta_id)
                st.success(f"✅ Se subieron {len(imagenes)} imagen(es) a tu carpeta de Drive.")
                st.write("📁 Carpeta:", carpeta_id)
    else:
        st.error("Correo no encontrado. Asegúrate de que el correo esté registrado en el formulario.")