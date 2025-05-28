# streamlit_app.py (estructura actualizada con buscador editable y columnas corregidas)
# Esta versión reemplaza el resumen por un panel con buscador y edición completa

import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime
import time
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ====== ESTILO VISUAL GENERAL ======
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
html, body, .block-container, .stApp {
    background-color: #e6e0f8 !important;
    font-family: 'Montserrat', sans-serif;
}
section[data-testid="stSidebar"], #MainMenu, header, footer {
    display: none !important;
}
.logo-container {
    display: flex;
    justify-content: center;
    margin-top: 30px;
    margin-bottom: 10px;
}
.logo-frame {
    background-color: white;
    padding: 10px;
    border-radius: 20px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    width: 60%;
    max-width: 600px;
    margin: auto;
}
.titulo {
    text-align: center;
    font-size: 24px;
    font-weight: bold;
    color: black;
    margin: 20px 0 10px 0;
    background-color: #cdb4f5;
    padding: 10px;
    border-radius: 10px;
}
.seccion {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-top: 30px;
    margin-bottom: 10px;
    border-bottom: 2px solid #bbb;
    padding-bottom: 5px;
}
input, textarea {
    font-family: 'Montserrat', sans-serif;
}
</style>
""", unsafe_allow_html=True)

# ============ CREDENCIALES GOOGLE SHEETS ============
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

# ============ AUTENTICACION ============
def buscar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# ============ LOGIN ============
if "auth_email" not in st.session_state:
    st.image("logo.png", use_container_width=True)
    correo = st.text_input("Correo electrónico").strip().lower()
    clave = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        user = buscar_usuario(correo)
        if not correo or not clave:
            st.warning("Debes completar ambos campos.")
        elif user is None:
            st.error("Correo no encontrado.")
        else:
            password_guardada = str(user.get("Contraseña", "")).strip().replace(",", "")
            password_introducida = clave.strip().replace(",", "")
            if not password_guardada:
                st.error("No hay contraseña configurada para este usuario.")
            elif password_guardada != password_introducida:
                st.error("Contraseña incorrecta.")
            else:
                st.session_state["auth_email"] = correo
                st.rerun()
else:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    # ============ PANELES DE ADMINISTRADOR ============
    if correo_usuario == ADMIN_EMAIL:
        st.markdown('<div class="seccion">BUSCADOR Y EDICIÓN DE DATOS</div>', unsafe_allow_html=True)
        busqueda = st.text_input("Buscar punto por cualquier campo (correo, nombre, teléfono, etc.)").lower().strip()

        df_filtrado = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(busqueda).any(), axis=1)] if busqueda else df

        if not df_filtrado.empty:
            for index, row in df_filtrado.iterrows():
                with st.expander(f"{row['Expendiduría']} - {row['Dirección de correo electrónico']}"):
                    with st.form(f"form_{index}"):
                        nuevos_valores = {}
                        for col in df.columns:
                            if "ultima actualización" not in col.lower():
                                nuevos_valores[col] = st.text_input(col, value=str(row[col]))
                        submitted = st.form_submit_button("Guardar cambios")
                        if submitted:
                            for col, new_value in nuevos_valores.items():
                                worksheet.update_cell(index+2, df.columns.get_loc(col)+1, new_value)
                            st.success("Datos actualizados correctamente.")
                            time.sleep(1)
                            st.rerun()
        else:
            st.info("No se encontraron resultados.")
