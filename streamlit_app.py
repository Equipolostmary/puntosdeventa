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

# ======== ESTILO VISUAL GENERAL ========
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
button[kind="primary"] {
    font-family: 'Montserrat', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# ============ AUTENTICACIÓN Y DATOS ============
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scopes)
client = gspread.authorize(creds)

sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
worksheet = sheet.worksheet("Registro")
df = pd.DataFrame(worksheet.get_all_records())

def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    st.markdown('<div class="seccion">ACCESO A RECURSOS</div>', unsafe_allow_html=True)
    enlaces = {...}  # Aquí van todos los enlaces como antes
    opcion = st.selectbox("Selecciona un recurso para abrir:", sorted(enlaces.keys()))
    if opcion:
        st.markdown(f"[Abrir {opcion} ▶️]({enlaces[opcion]})", unsafe_allow_html=True)

    if correo_usuario == ADMIN_EMAIL:
        st.markdown(f'<div class="titulo">ÁREA PRIVADA – ADMINISTRADOR</div>', unsafe_allow_html=True)
        st.markdown('<div class="seccion">🔎 BUSCAR Y EDITAR PUNTOS DE VENTA</div>', unsafe_allow_html=True)
        termino = st.text_input("Buscar por teléfono, correo, expendiduría o usuario").strip().lower()

        if termino:
            resultados = df[df.apply(lambda row: termino in str(row.get("TELÉFONO", "")).lower()
                                                or termino in str(row.get("Usuario", "")).lower()
                                                or termino in str(row.get("Expendiduría", "")).lower(), axis=1)]

            if not resultados.empty:
                st.info(f"{len(resultados)} resultado(s) encontrado(s).")
                opciones = [f"{row['Usuario']} - {row['Expendiduría']} - {row['TELÉFONO']}" for _, row in resultados.iterrows()]
                seleccion = st.selectbox("Selecciona un punto para editar:", opciones)
                index = resultados.index[opciones.index(seleccion)]

                with st.form(f"editar_usuario_{index}"):
                    nuevos_valores = {}
                    for col in df.columns:
                        if col != "Carpeta privada":
                            nuevos_valores[col] = st.text_input(col, str(df.at[index, col]), key=f"{col}_{index}")
                    guardar = st.form_submit_button("Guardar cambios")
                    if guardar:
                        try:
                            for col, nuevo_valor in nuevos_valores.items():
                                worksheet.update_cell(index + 2, df.columns.get_loc(col) + 1, nuevo_valor)
                            st.success("✅ Datos actualizados correctamente.")
                            time.sleep(2)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al guardar: {e}")
            else:
                st.warning("No se encontró ningún punto con ese dato.")
    else:
        user = buscar_usuario(correo_usuario)
        nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

        if user is None:
            st.error("Usuario no encontrado.")
            st.session_state.clear()
            st.rerun()

        st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)
        st.success(f"¡Bienvenido, {user['Expendiduría']}!")

        st.markdown('<div class="seccion">DATOS REGISTRADOS</div>', unsafe_allow_html=True)
        columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
        for col in columnas_visibles:
            if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
                etiqueta = "Usuario" if col.lower() == "usuario" else col
                st.markdown(f"**{etiqueta}:** {user.get(col, '')}")

        st.markdown('<div class="seccion">ESTADO DE PROMOCIONES</div>', unsafe_allow_html=True)
        def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
        tappo = val("Promoción 2+1 TAPPO")
        bm1000 = val("Promoción 3×21 BM1000")
        total = val("TOTAL PROMOS")
        entregados = val("REPUESTOS") if "REPUESTOS" in df.columns else 0
        pendientes = val("PENDIENTE DE REPONER") if "PENDIENTE DE REPONER" in df.columns else 0

        st.write(f"- TAPPO asignados: {tappo}")
        st.write(f"- BM1000 asignados: {bm1000}")
        st.write(f"- Total promociones acumuladas: {total}")
        st.write(f"- Promos entregadas: {entregados}")
        st.write(f"- Pendientes de entregar: {pendientes}")

        st.markdown('<div class="seccion">SUBIR NUEVAS PROMOCIONES</div>', unsafe_allow_html=True)
        if "widget_key_promos" not in st.session_state:
            st.session_state.widget_key_promos = str(uuid.uuid4())
        if "widget_key_imgs" not in st.session_state:
            st.session_state.widget_key_imgs = str(uuid.uuid4())

        promo1 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
        promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
        imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

        if st.button("SUBIR PROMOCIONES"):
            if not imagenes:
                st.warning("Selecciona al menos una imagen.")
            else:
                service = conectar_drive(st.secrets["gcp_service_account"])
                carpeta_id = str(user["Carpeta privada"]).split("/")[-1]
                ok = 0
                for img in imagenes:
                    try:
                        subir_archivo_a_drive(service, img, img.name, carpeta_id)
                        ok += 1
                    except Exception as e:
                        st.error(f"Error al subir {img.name}: {e}")
                if ok:
                    row = user.name + 2
                    worksheet.update_cell(row, df.columns.get_loc("Promoción 2+1 TAPPO")+1, str(tappo + promo1))
                    worksheet.update_cell(row, df.columns.get_loc("Promoción 3×21 BM1000")+1, str(bm1000 + promo2))
                    worksheet.update_cell(row, df.columns.get_loc("TOTAL PROMOS")+1, str(tappo + promo1 + bm1000 + promo2))
                    st.session_state.widget_key_promos = str(uuid.uuid4())
                    st.session_state.widget_key_imgs = str(uuid.uuid4())
                    st.success("✅ Imágenes subidas correctamente. Contadores actualizados.")
                    time.sleep(2)
                    st.rerun()

        st.markdown('<div class="seccion">INCENTIVO COMPENSACIONES MENSUALES</div>', unsafe_allow_html=True)
        objetivo = user.get("OBJETIVO", "")
        compensacion = user.get("COMPENSACION", "")
        ventas_mensuales = user.get("VENTAS MENSUALES", "")
        st.write(f"- OBJETIVO: {objetivo if objetivo else '*No asignado*'}")
        st.write(f"- COMPENSACIÓN: {compensacion if compensacion else '*No definido*'}")
        st.write(f"- Ventas acumuladas: {ventas_mensuales if ventas_mensuales else '*Sin registrar*'}")

        st.markdown('<div class="seccion">REPORTA TUS VENTAS</div>', unsafe_allow_html=True)
        if "widget_key_ventas" not in st.session_state:
            st.session_state.widget_key_ventas = str(uuid.uuid4())
        if "widget_key_fotos" not in st.session_state:
            st.session_state.widget_key_fotos = str(uuid.uuid4())

        with st.form("formulario_ventas"):
            cantidad = st.number_input("¿Cuántos dispositivos has vendido este mes?", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
            fotos = st.file_uploader("Sube fotos (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
            enviar = st.form_submit_button("Enviar")

        if enviar:
            if not fotos:
                st.warning("Debes subir al menos una imagen.")
            else:
                try:
                    col_destino = "VENTAS MENSUALES"
                    row = user.name + 2
                    col_index = df.columns.get_loc(col_destino) + 1
                    valor_anterior = user.get(col_destino, 0)
                    anterior = int(valor_anterior) if str(valor_anterior).isdigit() else 0
                    suma = anterior + int(cantidad)
                    worksheet.update_cell(row, col_index, str(suma))

                    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', user["Carpeta privada"])
                    carpeta_id = match.group(1) if match else None
                    if carpeta_id:
                        service = conectar_drive(st.secrets["gcp_service_account"])
                        for archivo in fotos:
                            subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

                    st.success("Ventas enviadas correctamente.")
                    time.sleep(2)
                    st.session_state.widget_key_ventas = str(uuid.uuid4())
                    st.session_state.widget_key_fotos = str(uuid.uuid4())
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al subir ventas: {e}")
else:
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
