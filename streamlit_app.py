import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
from google.oauth2.service_account import Credentials
from google_sheets import cargar_datos_hoja
from drive_upload import conectar_drive, subir_archivo_a_drive

# Configuración de la app
st.set_page_config(page_title="Área de Puntos Lost Mary", layout="centered")

# Estilos visuales
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #e0bbff, #ffcce6);
        font-family: 'Montserrat', sans-serif;
    }
    .stTextInput > div > input {
        font-size: 18px;
    }
    .stButton > button {
        font-size: 18px;
        padding: 8px 20px;
    }
    .promo-box {
        background-color: #ffffffdd;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
    }
    .promo-header {
        font-size: 28px;
        margin-bottom: 10px;
    }
    .promo-item {
        font-size: 20px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Logo
st.image("logo_lostmary.png", width=400)

# Formulario de inicio de sesión
st.header("Iniciar sesión")
correo = st.text_input("Correo electrónico").strip().lower()
clave = st.text_input("Contraseña", type="password")

if st.button("Acceder") or (correo and clave):
    # Cargar datos
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1a14wIe2893oS7zhicvT4mU0N_dM3vqItkTfJdHB325A"
    PESTAÑA = "Registro"
    datos = cargar_datos_hoja(SHEET_URL, pestaña=PESTAÑA)

    if correo in datos["Dirección de correo electrónico"].str.lower().values:
        punto = datos[datos["Dirección de correo electrónico"].str.lower() == correo].iloc[0]
        clave_correcta = str(punto["Contraseña"]).strip()

        if clave.strip() == clave_correcta:
            st.success("Sesión iniciada correctamente")

            # Datos personales
            st.markdown("### 👤 Datos del punto")
            for etiqueta, columna in [
                ("Expendiduría", "Expendiduría"),
                ("Dirección", "Dirección"),
                ("Código postal", "Código postal"),
                ("POBLACION", "POBLACION"),
                ("PROVINCIA", "PROVINCIA"),
                ("Número de teléfono", "Número de teléfono"),
                ("Nombre", "Nombre"),
                ("RESPONSABLE DE ZONA", "RESPONSABLE DE ZONA"),
            ]:
                st.markdown(f"**{etiqueta}:** {punto.get(columna, '')}")

            # Carpeta privada
            st.markdown(f"**Carpeta privada:** [Acceder]({punto['Carpeta privada']})")

            # Promociones
            st.markdown("### 📦 Estado de promociones")
            st.markdown('<div class="promo-box">', unsafe_allow_html=True)

            asignado_tappo = int(punto.get("Promoción 2+1 TAPPO", 0))
            entregado_tappo = int(punto.get("Entregados promo TAPPO", 0))
            pendiente_tappo = int(punto.get("Falta por entregar TAPPO", 0))

            asignado_bm = int(punto.get("Promoción 3×21 BM1000", 0))
            entregado_bm = int(punto.get("Entregados promo BM1000", 0))
            pendiente_bm = int(punto.get("Falta por entregar BM1000", 0))

            st.markdown(f"""
                <div class="promo-item">✅ <strong>TAPPO asignados:</strong> {asignado_tappo} | Entregados: {entregado_tappo} | ⏳ Pendientes: {pendiente_tappo}</div>
                <div class="promo-item">✅ <strong>BM1000 asignados:</strong> {asignado_bm} | Entregados: {entregado_bm} | ⏳ Pendientes: {pendiente_bm}</div>
            """, unsafe_allow_html=True)

            actualizacion = punto.get("Última actualización", "")
            st.markdown(f"<div class='promo-item'>🕓 <strong>Última actualización:</strong> {actualizacion}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Botón cerrar sesión
            if st.button("Cerrar sesión"):
                st.experimental_rerun()
        else:
            st.error("Contraseña incorrecta.")
    else:
        st.error("Correo no encontrado. Revisa si está bien escrito o si estás registrado.")
