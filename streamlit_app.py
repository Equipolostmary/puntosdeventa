import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from drive_upload import conectar_drive, subir_archivo_a_drive
from google_sheets import cargar_datos_hoja

# ✅ CONFIGURACIÓN INICIAL
st.set_page_config(page_title="Lost Mary - Área de Puntos", layout="centered")

# 🎨 DISEÑO: fondo azul claro + fuente Montserrat
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    html, body, [data-testid="stAppViewContainer"] {
        background-color: #e6f0ff;
        font-family: 'Montserrat', sans-serif;
        color: #0d1b2a;
    }

    h1, h2, h3, h4 {
        font-weight: 600;
        color: #06283D;
    }

    .stTextInput > div > div > input {
        font-size: 16px;
    }

    .stButton > button {
        font-size: 16px;
        font-weight: 600;
        padding: 0.5em 1em;
    }

    .stMarkdown, .stDataFrame {
        font-size: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# 🖼 LOGO Lost Mary
st.markdown("""
    <div style='text-align: center; margin-top: 20px; margin-bottom: 40px;'>
        <img src='https://drive.google.com/uc?export=view&id=1ucg7pCm0HWExIe_Gv7gu90EoS3Z31WBf' width='200'>
    </div>
""", unsafe_allow_html=True)

st.title("Área de Puntos de Venta")
st.write("Introduce tu correo para acceder a tu área personalizada:")

# 📄 CONFIG GOOGLE SHEET
SHEET_URL = "https://docs.google.com/spreadsheets/d/1a14wIe2893oS7zhicvT4mU0N_dM3vqItkTfJdHB325A"
PESTAÑA = "Registro"

@st.cache_data
def cargar_datos():
    return cargar_datos_hoja(SHEET_URL, pestaña=PESTAÑA)

# Entrada del correo
correo = st.text_input("Correo electrónico").strip().lower()

if correo:
    datos = cargar_datos()

    if correo in datos["Dirección de correo electrónico"].str.lower().values:
        punto = datos[datos["Dirección de correo electrónico"].str.lower() == correo].iloc[0]

        st.success(f"¡Bienvenido, {punto['Expendiduría']}!")

        try:
            # Conexión con Google Sheets
            SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
            service_account_info = st.secrets["gcp_service_account"]
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPE)
            client = gspread.authorize(creds)
            sheet = client.open_by_url(SHEET_URL)
            worksheet = sheet.worksheet(PESTAÑA)

            correos = worksheet.col_values(2)  # Dirección de correo electrónico (col B)
            fila_usuario = None

            for i, val in enumerate(correos):
                if val and isinstance(val, str) and val.strip().lower() == correo:
                    fila_usuario = i + 1
                    break

            if fila_usuario:
                # 📊 Mostrar solo hasta "Carpeta privada" (col L / índice 11)
                st.subheader("📋 Información del punto de venta")
                for col in datos.columns[:12]:
                    valor = punto[col]
                    st.markdown(f"**{col}:** {valor}")

                # 📦 Contadores de promociones
                val1 = worksheet.cell(fila_usuario, 13).value  # Col M
                val2 = worksheet.cell(fila_usuario, 14).value  # Col N

                total1 = int(val1) if val1 and val1.isnumeric() else 0
                total2 = int(val2) if val2 and val2.isnumeric() else 0

                st.info(f"📦 Promociones 2+1 TAPPO acumuladas: **{total1}**")
                st.info(f"📦 Promociones 3×21 BM1000 acumuladas: **{total2}**")

                # 📤 Subida de nuevas promociones
                st.subheader("📸 Subir nuevas promociones")
                promo1 = st.number_input("¿Cuántas promociones 2+1 TAPPO quieres registrar?", min_value=0, step=1)
                promo2 = st.number_input("¿Cuántas promociones 3×21 BM1000 quieres registrar?", min_value=0, step=1)
                imagenes = st.file_uploader("Sube las fotos de los tickets o promociones", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

                if st.button("Subir promociones"):
                    if not imagenes:
                        st.warning("Debes seleccionar al menos una imagen.")
                    else:
                        service = conectar_drive(st.secrets["gcp_service_account"])
                        carpeta_enlace = punto["Carpeta privada"]
                        carpeta_id = carpeta_enlace.split("/")[-1]

                        imagenes_ok = 0
                        for imagen in imagenes:
                            if not imagen.name or imagen.size == 0:
                                st.warning("Uno de los archivos está vacío o no tiene nombre.")
                                continue
                            try:
                                subir_archivo_a_drive(service, imagen, imagen.name, carpeta_id)
                                imagenes_ok += 1
                            except Exception as e:
                                st.error(f"❌ Error al subir {imagen.name}: {e}")

                        if imagenes_ok == 0:
                            st.stop()

                        # Actualizar contadores
                        val1 = worksheet.cell(fila_usuario, 13).value
                        val2 = worksheet.cell(fila_usuario, 14).value

                        total1 = int(val1) if val1 and val1.isnumeric() else 0
                        total2 = int(val2) if val2 and val2.isnumeric() else 0

                        nuevo1 = total1 + promo1
                        nuevo2 = total2 + promo2

                        worksheet.update_cell(fila_usuario, 13, str(nuevo1))
                        worksheet.update_cell(fila_usuario, 14, str(nuevo2))
                        worksheet.update_cell(fila_usuario, 15, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                        st.success(f"✅ Se subieron {imagenes_ok} imagen(es) y se actualizaron tus promociones.")
                        st.info(f"📦 2+1 TAPPO acumuladas: **{nuevo1}**")
                        st.info(f"📦 3×21 BM1000 acumuladas: **{nuevo2}**")
        except Exception as e:
            st.error("⚠️ Error al acceder a tu información.")
            st.text(str(e))
    else:
        st.error("Correo no encontrado. Asegúrate de que esté registrado en el formulario.")
