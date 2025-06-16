import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid
import re

# ===== CONFIGURACIÓN INICIAL =====
st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ===== ENLACES =====
enlaces = {
    "ACCIONES COMERCIALES Q4 2024": "https://docs.google.com/spreadsheets/d/1DqC1348Z3LqnzCVB8d8AqDbsAR3WUDUf/edit?gid=1142706501#gid=1142706501",
    "CATALOGO DE MATERIALES": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-YPxpn22EL6g/p/10ciZH8DpEsC5GNpYSigFrFJ_Fln9B0Q2/preview?authuser=0",
    # ... (otros enlaces permanecen igual)
}

# ============ ESTILO MEJORADO ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
:root {
    --color-primario: #6a3093;
    --color-secundario: #a044ff;
    --color-fondo: #f5f0ff;
    --color-texto: #333333;
    --color-texto-claro: #ffffff;
    --color-borde: #d1c4e9;
    --color-exito: #4caf50;
    --color-alerta: #ff9800;
    --color-error: #f44336;
}

html, body, .block-container, .stApp {
    background-color: var(--color-fondo) !important;
    font-family: 'Montserrat', sans-serif;
    color: var(--color-texto) !important;
}

section[data-testid="stSidebar"], #MainMenu, header, footer {
    display: none !important;
}

.logo-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

.logo-frame {
    background-color: white;
    padding: 15px;
    border-radius: 20px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    width: 70%;
    max-width: 400px;
    margin: 0 auto;
}

.titulo {
    text-align: center;
    font-size: 22px;
    font-weight: bold;
    color: var(--color-texto-claro);
    margin: 15px 0;
    background: linear-gradient(135deg, var(--color-primario), var(--color-secundario));
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.seccion {
    font-size: 16px;
    font-weight: bold;
    color: var(--color-primario);
    margin: 25px 0 10px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid var(--color-borde);
}

.card {
    background-color: white;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-title {
    font-weight: bold;
    color: var(--color-primario);
    margin-bottom: 10px;
    font-size: 16px;
}

.promo-card {
    background-color: #f3e5f5;
    border-left: 4px solid var(--color-primario);
}

.ventas-card {
    background-color: #e8f5e9;
    border-left: 4px solid var(--color-exito);
}

.link-button {
    color: var(--color-primario) !important;
    text-decoration: none !important;
    font-weight: bold !important;
    display: inline-block;
    margin: 5px 0;
}

.link-button:hover {
    text-decoration: underline !important;
}

.stButton>button {
    background: linear-gradient(135deg, var(--color-primario), var(--color-secundario)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-family: 'Montserrat', sans-serif !important;
}

.stNumberInput, .stTextInput, .stFileUploader {
    margin-bottom: 15px !important;
}

/* Forzar color de texto en todos los elementos */
* {
    color: var(--color-texto) !important;
}
</style>
""", unsafe_allow_html=True)

# ============ AUTENTICACIÓN Y DATOS ============
# (Mantener igual tu código actual de autenticación y conexión con Google Sheets)

# ===== FUNCIÓN PARA MOSTRAR ESTADO DE PROMOCIONES =====
def mostrar_estado_promociones(user):
    def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
    
    tappo = val(promo_tappo_col)
    bm1000 = val(promo_bm1000_col)
    tappo_2x1 = val(promo_tappo_2x1_col)
    total = tappo + bm1000 + tappo_2x1
    entregados = val("REPUESTOS") if "REPUESTOS" in df.columns else 0
    pendientes = val("PENDIENTE DE REPONER") if "PENDIENTE DE REPONER" in df.columns else 0
    
    with st.container():
        st.markdown('<div class="card promo-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 ESTADO DE PROMOCIONES</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("TAPPO 3x10", tappo)
            st.metric("BM1000 3×21", bm1000)
            st.metric("TAPPO 2+1", tappo_2x1)
        
        with col2:
            st.metric("Total Promociones", total)
            st.metric("Entregados", entregados, delta=f"{entregados-total}" if entregados != total else None)
            st.metric("Pendientes", pendientes, delta="reponer" if pendientes > 0 else None)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== FUNCIÓN PARA MOSTRAR ESTADO DE VENTAS =====
def mostrar_estado_ventas(user):
    objetivo = user.get("OBJETIVO", "")
    compensacion = user.get("COMPENSACION", "")
    ventas = user.get("VENTAS MENSUALES", "")
    
    with st.container():
        st.markdown('<div class="card ventas-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💰 INCENTIVO COMPENSACIONES MENSUALES</div>', unsafe_allow_html=True)
        
        if objetivo and str(objetivo).isdigit():
            progreso = int(ventas)/int(objetivo)*100 if ventas and str(ventas).isdigit() else 0
            st.progress(min(100, progreso))
            st.caption(f"Progreso: {min(100, round(progreso, 1))}% ({ventas if ventas else '0'}/{objetivo})")
        else:
            st.warning("Objetivo no definido")
        
        cols = st.columns(2)
        cols[0].metric("Compensación", compensacion if compensacion else "No definido")
        cols[1].metric("Ventas acumuladas", ventas if ventas else "Sin registrar")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ===== FUNCIÓN PARA MOSTRAR DATOS PERSONALES =====
def mostrar_datos_personales(user):
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👤 DATOS PERSONALES</div>', unsafe_allow_html=True)
        
        columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
        for col in columnas_visibles:
            if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
                etiqueta = "Usuario" if col.lower() == "usuario" else col
                valor = user.get(col, '')
                
                # Mostrar enlace para la carpeta privada
                if "carpeta privada" in col.lower() and valor.startswith("http"):
                    st.markdown(f"**{etiqueta}:** [Abrir carpeta privada]({valor})", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{etiqueta}:** {valor}")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    # Header con logo y título
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)

    # Botón de cierre de sesión
    if st.button("CERRAR SESIÓN", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    # Mostrar secciones principales
    mostrar_datos_personales(user)
    mostrar_estado_promociones(user)
    mostrar_estado_ventas(user)

    # Sección de ADMIN o USUARIO normal
    if correo_usuario == ADMIN_EMAIL:
        # Sección de recursos para ADMIN
        with st.expander("📂 RECURSOS COMPARTIDOS", expanded=False):
            opcion = st.selectbox("Selecciona un recurso:", sorted(enlaces.keys()), key="recursos_maestro")
            if opcion:
                st.markdown(f"[Abrir {opcion}]({enlaces[opcion]})", unsafe_allow_html=True)

        # Sección de búsqueda para ADMIN
        with st.expander("🔎 BUSCAR Y EDITAR PUNTOS DE VENTA", expanded=False):
            termino = st.text_input("Buscar por teléfono, correo o nombre").strip().lower()
            if termino:
                # (Mantener tu código actual de búsqueda y edición)
                pass
    else:
        # Sección para subir promociones (usuarios normales)
        with st.expander("📤 SUBIR NUEVAS PROMOCIONES", expanded=False):
            if "widget_key_promos" not in st.session_state:
                st.session_state.widget_key_promos = str(uuid.uuid4())
            if "widget_key_imgs" not in st.session_state:
                st.session_state.widget_key_imgs = str(uuid.uuid4())

            promo1 = st.number_input("Promos 3x13 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
            promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
            promo3 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_3")
            imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)

            if st.button("SUBIR PROMOCIONES", key="upload_promos_btn"):
                # (Mantener tu código actual de subida de promociones)
                pass

        # Sección para reportar ventas (usuarios normales)
        with st.expander("💳 REPORTAR VENTAS MENSUALES", expanded=False):
            if "widget_key_ventas" not in st.session_state:
                st.session_state.widget_key_ventas = str(uuid.uuid4())
            if "widget_key_fotos" not in st.session_state:
                st.session_state.widget_key_fotos = str(uuid.uuid4())

            with st.form("formulario_ventas"):
                cantidad = st.number_input("Dispositivos vendidos este mes", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
                fotos = st.file_uploader("Sube comprobantes", type=["jpg", "png"], accept_multired_files=True, key=st.session_state.widget_key_fotos)
                enviar = st.form_submit_button("ENVIAR VENTAS")

            if enviar:
                # (Mantener tu código actual de subida de ventas)
                pass

else:
    # Página de login (mantener similar pero con mejor estilo)
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        correo = st.text_input("Correo electrónico").strip().lower()
        clave = st.text_input("Contraseña", type="password")
        if st.form_submit_button("ACCEDER"):
            # (Mantener tu código actual de autenticación)
            pass
