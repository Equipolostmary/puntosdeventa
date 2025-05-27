import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
html, body, .block-container, .stApp, .main {
    background-color: #e6e0f8 !important;
    font-family: 'Montserrat', sans-serif;
}
section[data-testid="stSidebar"], #MainMenu, header, footer {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

def buscar_usuario(email):
    mask = df["Dirección de correo electrónico"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    st.image("logo.png", use_container_width=True)

    st.markdown(f"""
    <div style="background-color:#bda2e0;margin-top:10px;padding:12px;text-align:center;
                font-weight:bold;font-size:20px;color:black;border-radius:10px;">
        ÁREA PRIVADA – {nombre_usuario}
    </div>
    """, unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")

    st.subheader("📋 DATOS REGISTRADOS")
    columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
    for col in columnas_visibles:
        if "contraseña" not in col.lower():
            st.markdown(f"**{col}:** {user.get(col, '')}")

    st.markdown("---")
    st.subheader("📦 ESTADO DE PROMOCIONES")

    def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
    tappo_asig = val("Promoción 2+1 TAPPO")
    tappo_ent = val("Entregados promo TAPPO")
    tappo_falt = val("Falta por entregar TAPPO")
    bm_asig = val("Promoción 3×21 BM1000")
    bm_ent = val("Entregados promo BM1000")
    bm_falt = val("Falta por entregar BM1000")

    st.markdown(f"""
    - **TAPPO ASIGNADOS:** {tappo_asig} | ✅ ENTREGADOS: {tappo_ent} | ⏳ PENDIENTES: {tappo_falt}
    - **BM1000 ASIGNADOS:** {bm_asig} | ✅ ENTREGADOS: {bm_ent} | ⏳ PENDIENTES: {bm_falt}
    - 🕓 **ÚLTIMA ACTUALIZACIÓN:** {user.get('Ultima actualización', 'N/A')}
    """)

    if st.session_state.get("subida_ok"):
        st.success("✅ IMÁGENES SUBIDAS CORRECTAMENTE. CONTADORES ACTUALIZADOS.")
        time.sleep(2)
        st.session_state.pop("subida_ok")
        st.rerun()

    if "widget_key_promos" not in st.session_state:
        st.session_state.widget_key_promos = str(uuid.uuid4())
    if "widget_key_imgs" not in st.session_state:
        st.session_state.widget_key_imgs = str(uuid.uuid4())

    st.subheader("📸 SUBIR NUEVAS PROMOCIONES")
    promo1 = st.number_input("PROMOS 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
    promo2 = st.number_input("PROMOS 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
    imagenes = st.file_uploader("TICKETS O IMÁGENES", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

    if st.button("SUBIR PROMOCIONES"):
        if not imagenes:
            st.warning("SELECCIONA AL MENOS UNA IMAGEN.")
        else:
            service = conectar_drive(st.secrets["gcp_service_account"])
            carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
            ok = 0
            for img in imagenes:
                try:
                    subir_archivo_a_drive(service, img, img.name, carpeta_id)
                    ok += 1
                except Exception as e:
                    st.error(f"ERROR AL SUBIR {img.name}: {e}")
            if ok:
                row = user.name + 2
                worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(tappo_asig + promo1))
                worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(bm_asig + promo2))
                col_actualizacion = [c for c in df.columns if "actualiz" in c.lower()][0]
                worksheet.update_cell(row, df.columns.get_loc(col_actualizacion)+1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                st.session_state["subida_ok"] = True
                st.session_state.widget_key_promos = str(uuid.uuid4())
                st.session_state.widget_key_imgs = str(uuid.uuid4())
                st.rerun()

    st.markdown("---")
    st.header("💰 INCENTIVO COMPENSACIONES MENSUALES")

    objetivo = user.get("OBJETIVO", "")
    compensacion = user.get("COMPENSACION", "")
    ventas_mensuales = user.get("VENTAS MENSUALES", "")
    st.subheader("🎯 OBJETIVO Y COMPENSACIÓN MENSUAL")
    st.markdown(f"- **OBJETIVO:** {objetivo if objetivo else '*NO ASIGNADO*'}")
    st.markdown(f"- **COMPENSACIÓN:** {compensacion if compensacion else '*NO DEFINIDO*'}")
    st.markdown(f"**📊 VENTAS ACUMULADAS:** {ventas_mensuales if ventas_mensuales else '*SIN REGISTRAR*'}")

    st.subheader("📤 REPORTA TUS VENTAS")

    if "widget_key_ventas" not in st.session_state:
        st.session_state.widget_key_ventas = str(uuid.uuid4())
    if "widget_key_fotos" not in st.session_state:
        st.session_state.widget_key_fotos = str(uuid.uuid4())

    with st.form("formulario_ventas"):
        cantidad = st.number_input("¿CUÁNTOS DISPOSITIVOS HAS VENDIDO ESTE MES?", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
        fotos = st.file_uploader("SUBE FOTOS (TICKETS, VITRINAS...)", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
        enviar = st.form_submit_button("ENVIAR")

    if enviar:
        if not fotos:
            st.warning("DEBES SUBIR AL MENOS UNA IMAGEN.")
        else:
            try:
                col_destino = "VENTAS MENSUALES"
                row = user.name + 2
                col_index = df.columns.get_loc(col_destino) + 1

                valor_anterior = user.get(col_destino, 0)
                try:
                    anterior = int(valor_anterior)
                except:
                    anterior = 0
                suma = anterior + int(cantidad)

                worksheet.update_cell(row, col_index, str(suma))

                match = re.search(r'/folders/([a-zA-Z0-9_-]+)', user["Carpeta privada"])
                carpeta_id = match.group(1) if match else None
                if carpeta_id:
                    service = conectar_drive(st.secrets["gcp_service_account"])
                    for archivo in fotos:
                        subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

                st.success("✅ VENTAS ENVIADAS CORRECTAMENTE.")
                time.sleep(2)
                st.session_state.widget_key_ventas = str(uuid.uuid4())
                st.session_state.widget_key_fotos = str(uuid.uuid4())
                st.rerun()
            except Exception as e:
                st.error(f"ERROR AL SUBIR VENTAS: {e}")

    if correo_usuario == ADMIN_EMAIL:
        st.markdown("---")
        st.subheader("🗂️ RESUMEN MAESTRO DE PUNTOS DE VENTA")
        columnas_deseadas = [
            "Dirección de correo electrónico", "Contraseña",
            "Promoción 2+1 TAPPO", "Promoción 3×21 BM1000",
            "OBJETIVO", "VENTAS MENSUALES"
        ]
        columnas_existentes = [c for c in columnas_deseadas if c in df.columns]
        resumen_df = df[columnas_existentes].fillna("")
        st.dataframe(resumen_df, use_container_width=True)

else:
    st.image("logo.png", use_container_width=True)
    correo = st.text_input("CORREO ELECTRÓNICO").strip().lower()
    clave = st.text_input("CONTRASEÑA", type="password")
    if st.button("ACCEDER"):
        user = buscar_usuario(correo)
        if not correo or not clave:
            st.warning("DEBES COMPLETAR AMBOS CAMPOS.")
        elif user is None:
            st.error("CORREO NO ENCONTRADO.")
        else:
            password_guardada = str(user.get("Contraseña", "")).strip().replace(",", "")
            password_introducida = clave.strip().replace(",", "")
            if not password_guardada:
                st.error("NO HAY CONTRASEÑA CONFIGURADA PARA ESTE USUARIO.")
            elif password_guardada != password_introducida:
                st.error("CONTRASEÑA INCORRECTA.")
            else:
                st.session_state["auth_email"] = correo
                st.rerun()
