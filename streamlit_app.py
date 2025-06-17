import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2 import service_account
from drive_upload import conectar_drive, subir_archivo_a_drive
import time
import uuid
import re

st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered", initial_sidebar_state="collapsed")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ===== ENLACES =====
enlaces = {
    "ACCIONES COMERCIALES Q4 2024": "https://docs.google.com/spreadsheets/d/1DqC1348Z3LqnzCVB8d8AqDbsAR3WUDUf/edit?gid=1142706501#gid=1142706501",
    "CATALOGO DE MATERIALES": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-YPxpn22EL6g/p/10ciZH8DpEsC5GNpYSigFrFJ_Fln9B0Q2/preview?authuser=0",
    "COMPENSACIONES MENSUALES": "https://docs.google.com/spreadsheets/d/1CpHwmPrRYqqMtXrZBZV7-nQ0eEH6Z-RWtpnT84ZtVB0/edit?gid=128791843#gid=128791843",
    "CORREO ELECTRONICO": "https://email.ionos.es/appsuite/#!&app=io.ox/mail&folder=default0/INBOX",
    "EVENTOS": "https://docs.google.com/spreadsheets/d/1VTzXhfGb0d1kiuN4HuHrcotvy0HzOENCjLkeaV3FNA/edit?gid=0#gid=0",
    "EXCELL VACACIONES": "https://ideasoriginales4-my.sharepoint.com/:x:/r/personal/erselfbar_ioinvestigacion_com/Documents/PROYECTO%20LOST%20MERY%20-%20ELFBAR/1.%20VACACIONES%202025/Vacaciones%20Equipo%20Lost%20Mary%202025.xlsx?d=w98ae47bd4a4f4096ab0cb35f2183d6fb&csf=1&web=1&e=yNQTrb",
    "EXPENDIDURÍAS": "https://serviciostelematicosext.hacienda.gob.es/CMT/GestitabExt/Egeo/index.cshtml",
    "FOTOS COMPENSACIONES": "https://drive.google.com/drive/u/1/folders/18SxC9Wy9VTz-W2auyIBMwaVU6yRqsHXA",
    "FOTOS DE LOS TICKET": "https://drive.google.com/drive/u/1/folders/1GpG-NERdKzZVItqa5v7B88BW_UAmb_e4",
    "PERSONIO": "https://login.personio.com/login",
    "PRECIO BM600": "https://docs.google.com/spreadsheets/d/1F-TyJSI32sIBvZtXUkfFQ5P2rQQeXHNISx1u95vi4o/edit?gid=0#gid=0",
    "REALIZAR PEDIDO": "https://docs.google.com/spreadsheets/d/1IUeYNQg3Dx4NK45K6vrikRWNq3vkM8HXplH8Ymb8h3tI/edit?gid=2078407623#gid=2078407623",
    "REGISTRAR PUNTO DE VENTA": "https://docs.google.com/forms/d/e/1FAIpQLScTNcjTq0DU2xIjB1EcqbVpcVXWlKurBiNBZFDngN3fhmYb1_A/viewform",
    "RESPUESTAS FORMULARIOS": "https://drive.google.com/drive/folders/1eNhwJQBf6ZqkR2X76MQdEy3-Fj1WfVQX",
    "VIDEOS": "https://sites.google.com/u/0/d/11uRx7ac0-qOavsKwF27n-YPxpn22EL6g/p/1hzXetHR3hVMwCE-Z7A0GGsMmI7q3hqjT/preview?authuser=0",
    "VINILOS": "https://docs.google.com/spreadsheets/d/112hSu3vSu0wBMCvAuMGFsANoAV7v2vfskI0Xm4ArX3Oc/edit?gid=0#gid=0",
    "VISUALES": "https://drive.google.com/drive/folders/1qzXCVrBcAuebu2kpen9sQ8X85ZIDh68C",
    "WEB DE ESTANCOS": "https://sites.google.com/view/estancoslostmary",
    "INTRODUCCION TAPPO": "https://drive.google.com/drive/u/1/folders/18KFVvu3Fg3W_Gr5erYtAXiPPG3zAxg8L"
}

# ============ ESTILO MEJORADO ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap');
:root {
    --color-primario: #6a3093;
    --color-secundario: #a044ff;
    --color-fondo: #f5f3ff;
    --color-texto: #333333;
    --color-borde: #d1d5db;
    --color-exito: #10b981;
    --color-error: #ef4444;
    --color-advertencia: #f59e0b;
    --color-info: #3b82f6;
}

* {
    font-family: 'Montserrat', sans-serif !important;
}

html, body, .block-container, .stApp {
    background-color: var(--color-fondo) !important;
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
    padding: 15px 25px;
    border-radius: 16px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    width: 80%;
    max-width: 500px;
    margin: 0 auto;
}

.titulo {
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    color: white;
    margin: 20px auto;
    background: linear-gradient(135deg, var(--color-primario), var(--color-secundario));
    padding: 12px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    max-width: 90%;
}

.seccion {
    font-size: 18px;
    font-weight: 600;
    color: var(--color-primario);
    margin: 30px 0 15px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--color-borde);
}

.dato-usuario {
    background-color: white;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.dato-usuario strong {
    color: var(--color-primario);
}

.stButton>button {
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
}

button[kind="primary"] {
    background-color: var(--color-primario) !important;
    border-color: var(--color-primario) !important;
}

.stNumberInput, .stTextInput, .stSelectbox, .stFileUploader {
    margin-bottom: 16px !important;
}

.stSuccess {
    background-color: rgba(16, 185, 129, 0.1) !important;
    border-left: 4px solid var(--color-exito) !important;
}

.stError {
    background-color: rgba(239, 68, 68, 0.1) !important;
    border-left: 4px solid var(--color-error) !important;
}

.stWarning {
    background-color: rgba(245, 158, 11, 0.1) !important;
    border-left: 4px solid var(--color-advertencia) !important;
}

.stInfo {
    background-color: rgba(59, 130, 246, 0.1) !important;
    border-left: 4px solid var(--color-info) !important;
}

/* Estilo para los expanders */
.st-emotion-cache-1h9usn1.e1f1d6gn3 {
    background-color: white;
    border-radius: 8px;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid var(--color-borde);
}

/* Barra de progreso */
.progress-bar {
    transition: width 0.5s ease-in-out;
}

/* Botones mejorados */
.custom-button {
    transition: all 0.3s ease;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.custom-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Tarjetas de métricas */
.metric-card {
    background: white;
    border-radius: 10px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    margin-bottom: 15px;
}

.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--color-primario);
    margin: 5px 0;
}

.metric-label {
    font-size: 14px;
    color: #666;
}

/* Mejoras para móviles */
@media (max-width: 768px) {
    .logo-frame {
        width: 90%;
        padding: 10px 15px;
    }
    
    .titulo {
        font-size: 18px;
        padding: 10px 15px;
    }
    
    .seccion {
        font-size: 16px;
    }
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
df.columns = df.columns.str.strip()

# ===== CREAR CARPETAS AUTOMÁTICAMENTE SI FALTAN =====
ID_CARPETA_RAIZ = "1YgVIv7j_u38UuDpWnDzgGiqAvxpE-XXc"
service = conectar_drive(st.secrets["gcp_service_account"])
for idx, row in df.iterrows():
    enlace_actual = str(row.get("Carpeta privada", "")).strip()
    if not enlace_actual.startswith("https://drive.google.com/drive/folders/"):
        nombre_carpeta = f"{row.get('Expendiduría', 'Punto')} - {row.get('Usuario', 'SinUsuario')}"
        try:
            metadata = {
                "name": nombre_carpeta,
                "mimeType": "application/vnd.google-apps.folder",
                "parents": [ID_CARPETA_RAIZ]
            }
            carpeta = service.files().create(body=metadata, fields="id").execute()
            carpeta_id = carpeta.get("id")
            enlace = f"https://drive.google.com/drive/folders/{carpeta_id}"
            time.sleep(1)
            worksheet.update_cell(idx + 2, df.columns.get_loc("Carpeta privada") + 1, enlace)
            df.at[idx, "Carpeta privada"] = enlace
        except Exception as e:
            st.warning(f"No se pudo crear carpeta para {nombre_carpeta}: {e}")

# ===== FUNCIÓN PARA BUSCAR USUARIO POR EMAIL =====
def buscar_usuario(email):
    mask = df["Usuario"].astype(str).str.lower() == email.lower().strip()
    return df[mask].iloc[0] if mask.any() else None

# ===== DEFINICIÓN DE COLUMNAS DE PROMOCIÓN =====
promo_tappo_col = "Promoción 3x10 TAPPO"
promo_bm1000_col = "Promoción 3×21 BM1000"
promo_tappo_2x1_col = "2+1 TAPPO"
total_promos_col = "TOTAL PROMOS"

# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)

    if st.button("CERRAR SESIÓN", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()

    st.success(f"¡Bienvenido, {user['Expendiduría']}!")

    if correo_usuario == ADMIN_EMAIL:
        st.markdown('<div class="seccion">📂 RECURSOS</div>', unsafe_allow_html=True)
        opcion = st.selectbox("Selecciona un recurso para abrir:", sorted(enlaces.keys()), key="recursos_maestro")
        if opcion:
            st.markdown(f'<a href="{enlaces[opcion]}" target="_blank" style="text-decoration: none; color: var(--color-primario); font-weight: 500;">Ir al recurso seleccionado →</a>', unsafe_allow_html=True)

        st.markdown('<div class="seccion">🔎 BUSCAR Y EDITAR PUNTOS DE VENTA</div>', unsafe_allow_html=True)
        termino = st.text_input("Buscar por teléfono, correo, expendiduría o usuario", key="busqueda_admin").strip().lower()

        if termino:
            resultados = df[df.apply(lambda row: termino in str(row.get("TELÉFONO", "")).lower()
                                                or termino in str(row.get("Usuario", "")).lower()
                                                or termino in str(row.get("Expendiduría", "")).lower(), axis=1)]
            if not resultados.empty:
                opciones = [f"{row['Usuario']} - {row['Expendiduría']} - {row['TELÉFONO']}" for _, row in resultados.iterrows()]
                seleccion = st.selectbox("Selecciona un punto para editar:", opciones, key="buscador_admin")
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

        # ===== SECCIÓN DE MENSAJES MASIVOS =====
        st.markdown('<div class="seccion">📨 ENVIAR MENSAJES MASIVOS</div>', unsafe_allow_html=True)
        
        with st.expander("Enviar mensaje a todos los clientes"):
            mensaje = st.text_area("Escribe tu mensaje para todos los clientes:")
            if st.button("Enviar mensaje masivo"):
                try:
                    # Obtener todos los números de teléfono (columna H)
                    telefonos = df['TELÉFONO'].dropna().astype(str).tolist()
                    # Aquí iría la lógica para enviar los mensajes (Twilio, etc.)
                    st.success(f"Mensaje preparado para enviar a {len(telefonos)} clientes")
                    st.warning("Nota: La función de envío real necesita configuración con Twilio u otro servicio SMS")
                except Exception as e:
                    st.error(f"Error al preparar mensajes: {e}")

    else:
        # ===== SECCIÓN DE DATOS REGISTRADOS =====
        st.markdown('<div class="seccion">📋 DATOS REGISTRADOS</div>', unsafe_allow_html=True)

        with st.expander("Ver datos personales"):
            columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
            for col in columnas_visibles:
                if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
                    etiqueta = "Usuario" if col.lower() == "usuario" else col
                    valor = user.get(col, '')
                    st.markdown(f'<div class="dato-usuario"><strong>{etiqueta}:</strong> {valor}</div>', unsafe_allow_html=True)

        # Enlace a la carpeta privada
        if user.get("Carpeta privada"):
            st.markdown(f"""
            <div style="margin-top: 20px;">
                <a href="{user['Carpeta privada']}" target="_blank" style="text-decoration: none;">
                    <button style="background-color: var(--color-primario); color: white; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        📁 Abrir mi carpeta privada
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)

        # ===== SECCIÓN DE PROMOCIONES =====
        st.markdown('<div class="seccion">🎁 ESTADO DE PROMOCIONES</div>', unsafe_allow_html=True)
        def val(col): return int(user.get(col, 0)) if str(user.get(col)).isdigit() else 0
        tappo = val(promo_tappo_col)
        bm1000 = val(promo_bm1000_col)
        tappo_2x1 = val(promo_tappo_2x1_col)
        total = tappo + bm1000 + tappo_2x1
        entregados = val("REPUESTOS") if "REPUESTOS" in df.columns else 0
        pendientes = val("PENDIENTE DE REPONER") if "PENDIENTE DE REPONER" in df.columns else 0

        # Tarjetas de promociones
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="metric-card">'
                        f'<div class="metric-label">TAPPO</div>'
                        f'<div class="metric-value">{tappo}</div>'
                        f'</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card">'
                        f'<div class="metric-label">BM1000</div>'
                        f'<div class="metric-value">{bm1000}</div>'
                        f'</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card">'
                        f'<div class="metric-label">2+1 TAPPO</div>'
                        f'<div class="metric-value">{tappo_2x1}</div>'
                        f'</div>', unsafe_allow_html=True)

        # Resumen de promociones
        st.markdown(f'<div class="dato-usuario">'
                    f'<strong>Total promociones acumuladas:</strong> {total}<br>'
                    f'<strong>Promos entregadas:</strong> {entregados}<br>'
                    f'<strong>Pendientes de entregar:</strong> {pendientes}'
                    f'</div>', unsafe_allow_html=True)

        # ===== SECCIÓN PARA SUBIR PROMOCIONES =====
        st.markdown('<div class="seccion">📤 SUBIR NUEVAS PROMOCIONES</div>', unsafe_allow_html=True)
        if "widget_key_promos" not in st.session_state:
            st.session_state.widget_key_promos = str(uuid.uuid4())
        if "widget_key_imgs" not in st.session_state:
            st.session_state.widget_key_imgs = str(uuid.uuid4())

        with st.container():
            st.markdown('<div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
            promo1 = st.number_input("Promos 3x13 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
            promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
            promo3 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_3")
            imagenes = st.file_uploader("Sube los tickets o imágenes de comprobante", type=["jpg", "png", "jpeg"], accept_multiple_files=True, key=st.session_state.widget_key_imgs)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("📤 SUBIR PROMOCIONES", key="subir_promos_btn"):
                if not imagenes:
                    st.warning("⚠️ Por favor, selecciona al menos una imagen como comprobante.")
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
                        row = df[df["Usuario"] == user["Usuario"]].index[0] + 2
                        worksheet.update_cell(row, df.columns.get_loc(promo_tappo_col)+1, str(tappo + promo1))
                        worksheet.update_cell(row, df.columns.get_loc(promo_bm1000_col)+1, str(bm1000 + promo2))
                        worksheet.update_cell(row, df.columns.get_loc(promo_tappo_2x1_col)+1, str(tappo_2x1 + promo3))
                        nuevo_total = tappo + promo1 + bm1000 + promo2 + tappo_2x1 + promo3
                        worksheet.update_cell(row, df.columns.get_loc(total_promos_col)+1, str(nuevo_total))
                        st.session_state.widget_key_promos = str(uuid.uuid4())
                        st.session_state.widget_key_imgs = str(uuid.uuid4())
                        st.success("✅ Imágenes subidas correctamente y contadores actualizados.")
                        time.sleep(2)
                        st.rerun()

# ===== SECCIÓN DE INCENTIVOS =====
st.markdown('<div class="seccion">💰 INCENTIVO COMPENSACIONES MENSUALES</div>', unsafe_allow_html=True)

# Obtener datos del usuario
objetivo = user.get("OBJETIVO", "0")
compensacion = user.get("COMPENSACION", "0")
ventas_mensuales = user.get("VENTAS MENSUALES", "0")

# Procesar los datos de compensación (eliminar saltos de línea y espacios extra)
compensacion_limpia = " ".join(compensacion.split())

try:
    objetivo_num = float(objetivo) if objetivo else 0
    ventas_num = float(ventas_mensuales) if ventas_mensuales else 0
    porcentaje = min(100, (ventas_num / objetivo_num * 100)) if objetivo_num > 0 else 0
except:
    porcentaje = 0

# Mostrar la información de incentivos
st.markdown(f"""
<div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
        <div style="flex: 1; margin-right: 10px;">
            <strong>OBJETIVO:</strong> {objetivo if objetivo else "No asignado"}
        </div>
        <div style="flex: 1;">
            <strong>COMPENSACIÓN:</strong> {compensacion_limpia if compensacion else "No definido"}
        </div>
    </div>
    
    <div style="margin-bottom: 5px;">
        <strong>Ventas acumuladas:</strong> {ventas_mensuales if ventas_mensuales else "0"}
    </div>
    
    <div style="background: #f0f0f0; border-radius: 10px; height: 20px; margin-bottom: 10px;">
        <div style="background: var(--color-primario); width: {porcentaje}%; height: 100%; border-radius: 10px; 
             display: flex; align-items: center; justify-content: center; color: white; font-size: 12px;">
            {round(porcentaje, 1)}%
        </div>
    </div>
    
    <div style="text-align: center; font-size: 14px; color: #666;">
        Progreso hacia el objetivo
    </div>
</div>
""", unsafe_allow_html=True)

        # ===== SECCIÓN DE REPORTE DE VENTAS =====
        st.markdown('<div class="seccion">📈 REPORTAR VENTAS MENSUALES</div>', unsafe_allow_html=True)
        if "widget_key_ventas" not in st.session_state:
            st.session_state.widget_key_ventas = str(uuid.uuid4())
        if "widget_key_fotos" not in st.session_state:
            st.session_state.widget_key_fotos = str(uuid.uuid4())

        with st.form("formulario_ventas", clear_on_submit=True):
            st.markdown('<div style="background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
            cantidad = st.number_input("¿Cuántos dispositivos has vendido este mes?", min_value=0, step=1, key=st.session_state.widget_key_ventas + "_cantidad")
            fotos = st.file_uploader("Sube fotos como comprobante (tickets, vitrinas...)", type=["jpg", "png"], accept_multiple_files=True, key=st.session_state.widget_key_fotos)
            enviar = st.form_submit_button("📤 ENVIAR REPORTE")
            st.markdown('</div>', unsafe_allow_html=True)

        if enviar:
            if not fotos:
                st.warning("⚠️ Debes subir al menos una imagen como comprobante.")
            else:
                try:
                    col_destino = "VENTAS MENSUALES"
                    row = df[df["Usuario"] == user["Usuario"]].index[0] + 2
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

                    st.success("✅ Ventas reportadas correctamente.")
                    time.sleep(2)
                    st.session_state.widget_key_ventas = str(uuid.uuid4())
                    st.session_state.widget_key_fotos = str(uuid.uuid4())
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al subir ventas: {e}")

else:
    # ===== PANTALLA DE LOGIN =====
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if "recover_password" not in st.session_state:
        st.session_state.recover_password = False

    if not st.session_state.recover_password:
        with st.form("login_form"):
            st.markdown('<div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: 600; color: var(--color-primario);">INICIAR SESIÓN</div>', unsafe_allow_html=True)
            correo = st.text_input("Correo electrónico", key="login_email").strip().lower()
            clave = st.text_input("Contraseña", type="password", key="login_pass")
            submit = st.form_submit_button("ACCEDER", type="primary")

            st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" onclick="alert('Se enviará un enlace de recuperación a tu correo');" 
                   style="color: var(--color-primario); text-decoration: none; font-size: 14px;">
                   ¿Olvidaste tu contraseña?
                </a>
            </div>
            """, unsafe_allow_html=True)

        if submit:
            user = buscar_usuario(correo)
            if not correo or not clave:
                st.warning("⚠️ Debes completar ambos campos.")
            elif user is None:
                st.error("❌ Correo no encontrado.")
            else:
                password_guardada = str(user.get("Contraseña", "")).strip().replace(",", "")
                password_introducida = clave.strip().replace(",", "")
                if not password_guardada:
                    st.error("❌ No hay contraseña configurada para este usuario.")
                elif password_guardada != password_introducida:
                    st.error("❌ Contraseña incorrecta.")
                else:
                    st.session_state["auth_email"] = correo
                    st.rerun()
    else:
        with st.form("recover_form"):
            st.markdown('<div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: 600; color: var(--color-primario);">RECUPERAR CONTRASEÑA</div>', unsafe_allow_html=True)
            recover_email = st.text_input("Ingresa tu correo electrónico", key="recover_email").strip().lower()
            submit_recover = st.form_submit_button("ENVIAR ENLACE")
            
            if submit_recover:
                user = buscar_usuario(recover_email)
                if user is not None:
                    # Aquí iría la lógica para enviar el correo de recuperación
                    st.success("Se ha enviado un enlace de recuperación a tu correo")
                    st.session_state.recover_password = False
                else:
                    st.error("Correo no encontrado")
