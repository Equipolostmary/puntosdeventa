import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import time
import uuid
import re
import io

# ===== CONFIGURACIÓN INICIAL =====
st.set_page_config(page_title="Lost Mary - Área Privada", layout="centered")
ADMIN_EMAIL = "equipolostmary@gmail.com"

# ===== FUNCIONES AUXILIARES =====
def conectar_drive(credenciales):
    """Conectar con Google Drive"""
    return build('drive', 'v3', credentials=credenciales)

def subir_archivo_a_drive(service, archivo, nombre_archivo, carpeta_id):
    """Subir archivo a Google Drive"""
    file_metadata = {
        'name': nombre_archivo,
        'parents': [carpeta_id]
    }
    media = MediaIoBaseUpload(io.BytesIO(archivo.read()), 
                            mimetype=archivo.type, 
                            resumable=True)
    file = service.files().create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
    return file.get('id')

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

# ===== ESTILO =====
st.markdown("""
<style>
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

* {
    color: var(--color-texto) !important;
}
</style>
""", unsafe_allow_html=True)

# ===== CONEXIÓN CON GOOGLE SHEETS =====
try:
    scopes = ["https://www.googleapis.com/auth/spreadsheets", 
             "https://www.googleapis.com/auth/drive"]
    
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(st.secrets["gcp_service_account"]["sheet_id"])
    worksheet = sheet.worksheet("Registro")
    df = pd.DataFrame(worksheet.get_all_records())
    df.columns = df.columns.str.strip()
    
    # Columnas de promoción
    promo_tappo_col = "Promoción 3x10 TAPPO"
    promo_bm1000_col = "Promoción 3×21 BM1000"
    promo_tappo_2x1_col = "2+1 TAPPO"
    total_promos_col = "TOTAL PROMOS"

except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# ===== FUNCIONES PARA MOSTRAR CONTENIDO =====
def mostrar_datos_personales(user):
    """Mostrar los datos personales del usuario"""
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">👤 DATOS PERSONALES</div>', unsafe_allow_html=True)
        
        columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
        for col in columnas_visibles:
            if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
                etiqueta = "Usuario" if col.lower() == "usuario" else col
                valor = user.get(col, '')
                
                if "carpeta privada" in col.lower() and valor.startswith("http"):
                    st.markdown(f"**{etiqueta}:** [Abrir carpeta privada]({valor})", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{etiqueta}:** {valor}")
        
        st.markdown('</div>', unsafe_allow_html=True)

def mostrar_estado_promociones(user):
    """Mostrar el estado de las promociones"""
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

def mostrar_estado_ventas(user):
    """Mostrar el estado de ventas y compensaciones"""
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

# ===== CREAR CARPETAS AUTOMÁTICAMENTE SI FALTAN =====
ID_CARPETA_RAIZ = "1YgVIv7j_u38UuDpWnDzgGiqAvxpE-XXc"
try:
    service = conectar_drive(creds)
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
except Exception as e:
    st.warning(f"Error al verificar carpetas: {e}")

# ===== INTERFAZ DE USUARIO PRINCIPAL =====
if "auth_email" not in st.session_state:
    # Página de login
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        correo = st.text_input("Correo electrónico").strip().lower()
        clave = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("ACCEDER"):
            if not correo or not clave:
                st.warning("Debes completar ambos campos.")
            else:
                user = buscar_usuario(correo)
                if user is None:
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
    # Área privada
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    
    if user is None:
        st.error("Usuario no encontrado en los registros.")
        st.session_state.clear()
        st.rerun()
    
    nombre_usuario = user["Expendiduría"] if "Expendiduría" in user else correo_usuario

    # Header
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)

    # Botón de cierre de sesión
    if st.button("CERRAR SESIÓN"):
        st.session_state.clear()
        st.rerun()

    # Mostrar secciones principales
    mostrar_datos_personales(user)
    mostrar_estado_promociones(user)
    mostrar_estado_ventas(user)

    # Sección específica para ADMIN
    if correo_usuario == ADMIN_EMAIL:
        with st.expander("📂 RECURSOS COMPARTIDOS", expanded=False):
            opcion = st.selectbox("Selecciona un recurso:", sorted(enlaces.keys()))
            if opcion:
                st.markdown(f"[Abrir {opcion}]({enlaces[opcion]})", unsafe_allow_html=True)

        with st.expander("🔎 BUSCAR Y EDITAR PUNTOS DE VENTA", expanded=False):
            termino = st.text_input("Buscar por teléfono, correo o nombre").strip().lower()
            if termino:
                resultados = df[df.apply(lambda row: 
                    termino in str(row.get("TELÉFONO", "")).lower() or
                    termino in str(row.get("Usuario", "")).lower() or
                    termino in str(row.get("Expendiduría", "")).lower(), axis=1)]
                
                if not resultados.empty:
                    opciones = [f"{row['Usuario']} - {row['Expendiduría']} - {row['TELÉFONO']}" 
                              for _, row in resultados.iterrows()]
                    seleccion = st.selectbox("Selecciona un punto para editar:", opciones)
                    index = resultados.index[opciones.index(seleccion)]
                    
                    with st.form(f"editar_usuario_{index}"):
                        nuevos_valores = {}
                        for col in df.columns:
                            if col != "Carpeta privada":
                                nuevos_valores[col] = st.text_input(col, str(df.at[index, col]))
                        
                        if st.form_submit_button("Guardar cambios"):
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
        # Sección para usuarios normales - Subir promociones
        with st.expander("📤 SUBIR NUEVAS PROMOCIONES", expanded=False):
            if "widget_key_promos" not in st.session_state:
                st.session_state.widget_key_promos = str(uuid.uuid4())
            if "widget_key_imgs" not in st.session_state:
                st.session_state.widget_key_imgs = str(uuid.uuid4())

            promo1 = st.number_input("Promos 3x13 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
            promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
            promo3 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_3")
            imagenes = st.file_uploader("Tickets o imágenes", type=["jpg", "png", "jpeg"], 
                                      accept_multiple_files=True, key=st.session_state.widget_key_imgs)

            if st.button("SUBIR PROMOCIONES"):
                if not imagenes:
                    st.warning("Selecciona al menos una imagen.")
                else:
                    try:
                        service = conectar_drive(creds)
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
                            st.success("✅ Imágenes subidas correctamente. Contadores actualizados.")
                            time.sleep(2)
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error en el proceso de subida: {e}")

        # Sección para usuarios normales - Reportar ventas
        with st.expander("💳 REPORTAR VENTAS MENSUALES", expanded=False):
            if "widget_key_ventas" not in st.session_state:
                st.session_state.widget_key_ventas = str(uuid.uuid4())
            if "widget_key_fotos" not in st.session_state:
                st.session_state.widget_key_fotos = str(uuid.uuid4())

            with st.form("formulario_ventas"):
                cantidad = st.number_input("Dispositivos vendidos este mes", min_value=0, step=1, 
                                         key=st.session_state.widget_key_ventas + "_cantidad")
                fotos = st.file_uploader("Sube comprobantes", type=["jpg", "png"], 
                                       accept_multiple_files=True, key=st.session_state.widget_key_fotos)
                enviar = st.form_submit_button("ENVIAR VENTAS")

            if enviar:
                if not fotos:
                    st.warning("Debes subir al menos una imagen.")
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
                            service = conectar_drive(creds)
                            for archivo in fotos:
                                subir_archivo_a_drive(service, archivo, archivo.name, carpeta_id)

                        st.success("Ventas enviadas correctamente.")
                        time.sleep(2)
                        st.session_state.widget_key_ventas = str(uuid.uuid4())
                        st.session_state.widget_key_fotos = str(uuid.uuid4())
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al subir ventas: {e}")
