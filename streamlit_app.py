import streamlit as st
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import datetime
from PIL import Image

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Lost Mary - Zona Privada", layout="centered")

# --- CARGA LOGO Y FONDO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f5efff;
        font-family: 'Montserrat', sans-serif;
    }
    .title-style {
        font-size: 28px;
        font-weight: 700;
        color: #3a0ca3;
        text-align: center;
        margin-top: 1em;
    }
    </style>
""", unsafe_allow_html=True)

st.image("logo.png", width=400)

# --- AUTENTICACIÓN ---
correo = st.text_input("Correo electrónico")
clave = st.text_input("Contraseña", type="password")
if st.button("Acceder") or (correo and clave):
    try:
        gcp_secrets = st.secrets["gcp_service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets",
                 "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(gcp_secrets, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(st.secrets["sheet_id"]).worksheet("Registro")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        if correo in df['dirección de correo electrónico'].values:
            punto = df[df['dirección de correo electrónico'] == correo].iloc[0]
            if str(punto['contraseña']).strip() == clave.strip():

                st.success(f"Bienvenido, {correo}")

                # --- INFORMACIÓN PERSONAL ---
                st.subheader("Información personal")
                st.markdown(f"**Expendiduría:** {punto['expendiduría']}")
                st.markdown(f"**Dirección:** {punto['dirección']}")
                st.markdown(f"**Código postal:** {punto['código postal']}")
                st.markdown(f"**POBLACION:** {punto['POBLACION']}")
                st.markdown(f"**PROVINCIA:** {punto['PROVINCIA']}")
                st.markdown(f"**Número de teléfono:** {punto['número de teléfono']}")
                st.markdown(f"**Nombre:** {punto['nombre']}")
                st.markdown(f"**RESPONSABLE DE ZONA:** {punto['RESPONSABLE DE ZONA']}")
                st.markdown(f"**Carpeta privada:** [Acceder]({punto['carpeta privada']})")

                # --- ESTADO DE PROMOCIONES ---
                st.subheader("🏢 Estado de promociones")
                promos = {
                    "TAPPO": {
                        "asignado": int(punto.get("promoción 2+1 tappo", 0)),
                        "entregado": int(punto.get("entregados promo tappo", 0))
                    },
                    "BM1000": {
                        "asignado": int(punto.get("promoción 3×21 bm1000", 0)),
                        "entregado": int(punto.get("entregados promo bm1000", 0))
                    }
                }
                for k, v in promos.items():
                    pendientes = v["asignado"] - v["entregado"]
                    st.markdown(f"- **{k} asignados:** {v['asignado']} 👉 💚 Entregados: {v['entregado']} 🕰 Pendientes: {pendientes}")

                ultima = punto.get("última actualización", "-")
                st.markdown(f"- 🔎 **Última actualización:** {ultima}")

                if st.button("Cerrar sesión"):
                    st.session_state.clear()
                    st.experimental_rerun()
            else:
                st.error("Contraseña incorrecta.")
        else:
            st.error("Usuario no registrado.")

    except Exception as e:
        st.error("Ha ocurrido un error en el acceso.")
        st.stop()
