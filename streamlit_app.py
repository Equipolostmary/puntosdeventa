import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Área Privada - Lost Mary", layout="centered")

# Estilos personalizados
st.markdown("""
    <style>
        body {
            background-color: #f3f0ff;
            font-family: 'Montserrat', sans-serif;
        }
        .stTextInput input {
            background-color: white;
            color: black;
        }
        .stButton button {
            background-color: #b47bff;
            color: white;
            font-weight: bold;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Mostrar logo
st.image("logo.png", use_column_width=True)

# Autenticación con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(st.secrets["sheet_id"]).worksheet("Registro")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# Función auxiliar
def seguro_a_int(valor):
    try:
        return int(valor)
    except:
        return 0

# Login
st.subheader("Iniciar sesión")
correo = st.text_input("Correo electrónico")
clave = st.text_input("Contraseña", type="password")
login_btn = st.button("Acceder")

if login_btn and correo:
    correo = correo.strip().lower()
    punto = df[df["Dirección de correo electrónico"].str.lower() == correo]
    if not punto.empty:
        punto = punto.iloc[0]
        if str(punto.get("Contraseña", "")).strip() == clave:
            st.success(f"Bienvenido, {correo}")
            st.markdown("---")

            # Mostrar datos personales
            campos_visibles = [
                "Marca temporal", "Expendiduría", "Dirección", "Código postal", "POBLACION",
                "PROVINCIA", "Número de teléfono", "Nombre", "RESPONSABLE DE ZONA", "Carpeta privada"
            ]
            for campo in campos_visibles:
                valor = punto.get(campo, "")
                st.markdown(f"**{campo}:** {valor}")

            # Mostrar estado de promociones
            st.markdown("### 📦 Estado de promociones")
            promos = {
                "TAPPO": {
                    "asignadas": seguro_a_int(punto.get("Promoción 2+1 TAPPO")),
                    "entregadas": seguro_a_int(punto.get("Entregados promo TAPPO")),
                    "faltan": seguro_a_int(punto.get("FALTA POR ENTREGAR TAPPO"))
                },
                "BM1000": {
                    "asignadas": seguro_a_int(punto.get("Promoción 3×21 BM1000")),
                    "entregadas": seguro_a_int(punto.get("Entregados promo BM1000")),
                    "faltan": seguro_a_int(punto.get("FALTA POR ENTREGAR BM1000"))
                }
            }

            for k, promo in promos.items():
                st.markdown(
                    f"- **{k} asignados:** {promo['asignadas']} | ✅ Entregados: {promo['entregados']} | ⏳ Pendientes: {promo['faltan']}"
                )

            ultima = punto.get("Última actualización", "")
            st.markdown(f"- 🕐 **Última actualización:** {ultima}")
        else:
            st.error("Contraseña incorrecta.")
    else:
        st.error("Correo no encontrado.")
