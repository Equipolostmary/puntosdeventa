import streamlit as st
import pandas as pd
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
    --color-primary: #6a3093;
    --color-secondary: #a044ff;
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
    margin: 10px 0;
}

.logo-frame {
    background-color: white;
    padding: 10px 20px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: 80%;
    max-width: 400px;
    margin: 0 auto;
}

.titulo {
    text-align: center;
    font-size: 20px;
    font-weight: 700;
    color: white;
    margin: 15px auto;
    background: linear-gradient(135deg, var(--color-primary), var(--color-secondary));
    padding: 10px 15px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    max-width: 90%;
}

.seccion {
    font-size: 16px;
    font-weight: 600;
    color: var(--color-primary);
    margin: 20px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--color-borde);
}

.dato-usuario {
    background-color: white;
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    font-size: 14px;
}

.dato-usuario strong {
    color: var(--color-primary);
}

.stButton>button {
    border-radius: 8px !important;
    padding: 8px 16px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    transition: all 0.2s ease !important;
}

.stButton>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1) !important;
}

button[kind="primary"] {
    background-color: var(--color-primary) !important;
    border-color: var(--color-primary) !important;
}

.stNumberInput, .stTextInput, .stSelectbox, .stFileUploader {
    margin-bottom: 12px !important;
}

.stSuccess {
    background-color: rgba(16, 185, 129, 0.1) !important;
    border-left: 3px solid var(--color-exito) !important;
    padding: 10px !important;
    font-size: 14px !important;
}

.stError {
    background-color: rgba(239, 68, 68, 0.1) !important;
    border-left: 3px solid var(--color-error) !important;
    padding: 10px !important;
    font-size: 14px !important;
}

.stWarning {
    background-color: rgba(245, 158, 11, 0.1) !important;
    border-left: 3px solid var(--color-advertencia) !important;
    padding: 10px !important;
    font-size: 14px !important;
}

.stInfo {
    background-color: rgba(59, 130, 246, 0.1) !important;
    border-left: 3px solid var(--color-info) !important;
    padding: 10px !important;
    font-size: 14px !important;
}

.promo-card {
    background: white;
    border-radius: 8px;
    padding: 10px 5px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    min-height: 70px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    margin: 0 2px;
}

.promo-value {
    font-size: 16px;
    font-weight: bold;
    color: var(--color-primary);
    margin: 5px 0;
}

.promo-label {
    font-size: 11px;
    color: #666;
    line-height: 1.2;
}

.promo-total {
    background-color: white;
    padding: 12px;
    border-radius: 8px;
    margin-top: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    font-size: 14px;
}

.sales-card {
    background: white;
    border-radius: 8px;
    padding: 15px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    margin-bottom: 15px;
    border-left: 4px solid var(--color-primary);
}

.sales-value {
    font-size: 24px;
    font-weight: bold;
    color: var(--color-primary);
    margin: 5px 0;
}

.sales-label {
    font-size: 14px;
    color: #666;
    margin-bottom: 5px;
}

.sales-target {
    font-size: 12px;
    color: #888;
}

.progress-container {
    margin: 15px 0;
}

.progress-bar {
    height: 20px;
    background: #e0e0e0;
    border-radius: 10px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
    border-radius: 10px;
    transition: width 0.5s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 12px;
    font-weight: bold;
}

.logout-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 100;
}

.logout-btn button {
    padding: 6px 12px !important;
    font-size: 12px !important;
    background-color: #f8f9fa !important;
    color: #dc3545 !important;
    border: 1px solid #dc3545 !important;
}

@media (max-width: 768px) {
    .logo-frame {
        width: 95%;
        padding: 6px 10px;
    }
    
    .titulo {
        font-size: 16px;
        padding: 6px 10px;
        margin: 8px auto;
    }
    
    .seccion {
        font-size: 13px;
        margin: 12px 0 6px 0;
    }
    
    .promo-card {
        padding: 8px 4px !important;
        min-height: 55px !important;
        margin: 0 1px !important;
    }
    
    .promo-value {
        font-size: 14px !important;
        margin: 3px 0 !important;
    }
    
    .promo-label {
        font-size: 9px !important;
        line-height: 1.1 !important;
    }
    
    .promo-total {
        font-size: 12px !important;
        padding: 8px 10px !important;
    }
    
    .sales-card {
        padding: 10px;
    }
    
    .sales-value {
        font-size: 18px;
    }
    
    .sales-label {
        font-size: 12px;
    }
    
    .sales-target {
        font-size: 11px;
    }
    
    .dato-usuario {
        padding: 8px 10px;
        font-size: 13px;
    }
    
    .logout-btn {
        position: fixed;
        bottom: 10px;
        right: 10px;
        width: auto;
    }
    
    .logout-btn button {
        padding: 5px 10px !important;
        font-size: 11px !important;
        max-width: 120px;
    }
    
    .stNumberInput, .stTextInput, .stSelectbox {
        margin-bottom: 6px !important;
    }
    
    .stButton>button {
        padding: 5px 10px !important;
        font-size: 12px !important;
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
service = conectar_drive()
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

def to_float(value):
    try:
        cleaned = ''.join(c for c in str(value) if c.isdigit() or c == '.')
        return float(cleaned) if cleaned else 0.0
    except:
        return 0.0

# ===== DEFINICIÓN DE COLUMNAS DE PROMOCIÓN =====
promo_tappo_col = "Promoción 3x10 TAPPO"
promo_bm1000_col = "Promoción 3×21 BM1000"
promo_tappo_2x1_col = "2+1 TAPPO"
total_promos_col = "TOTAL PROMOS"

# ============ ÁREA PRIVADA ============
if "auth_email" in st.session_state:
    correo_usuario = st.session_state["auth_email"]
    user = buscar_usuario(correo_usuario)
    
    if user is None:
        st.error("Usuario no encontrado.")
        st.session_state.clear()
        st.rerun()
    
    nombre_usuario = user["Expendiduría"] if user is not None else correo_usuario

    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)  # Cambiado de use_column_width a use_container_width
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="titulo">ÁREA PRIVADA – {nombre_usuario}</div>', unsafe_allow_html=True)

    if correo_usuario == ADMIN_EMAIL:
        # ===== PANEL DE ADMINISTRADOR =====
        st.markdown('<div class="seccion">RECURSOS</div>', unsafe_allow_html=True)  # Eliminado el emoji
        opcion = st.selectbox("Selecciona un recurso para abrir:", sorted(enlaces.keys()), key="recursos_maestro")
        if opcion:
            st.markdown(f'<a href="{enlaces[opcion]}" target="_blank" style="text-decoration: none; color: var(--color-primary); font-weight: 500;">Ir al recurso seleccionado →</a>', unsafe_allow_html=True)

        st.markdown('<div class="seccion">BUSCAR Y EDITAR PUNTOS DE VENTA</div>', unsafe_allow_html=True)  # Eliminado el emoji
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
        st.markdown('<div class="seccion">ENVIAR MENSAJES MASIVOS</div>', unsafe_allow_html=True)  # Eliminado el emoji
        with st.expander("Enviar mensaje a todos los clientes"):
            mensaje = st.text_area("Escribe tu mensaje para todos los clientes:")
            if st.button("Enviar mensaje masivo"):
                try:
                    telefonos = df['TELÉFONO'].dropna().astype(str).tolist()
                    st.success(f"Mensaje preparado para enviar a {len(telefonos)} clientes")
                    st.warning("Nota: La función de envío real necesita configuración con Twilio u otro servicio SMS")
                except Exception as e:
                    st.error(f"Error al preparar mensajes: {e}")

    else:
        # ===== PANEL DE USUARIO =====
        with st.expander("MIS DATOS", expanded=False):  # Eliminado el emoji
            columnas_visibles = list(df.columns[:df.columns.get_loc("Carpeta privada")+1])
            for col in columnas_visibles:
                if "contraseña" not in col.lower() and "marca temporal" not in col.lower():
                    etiqueta = "Usuario" if col.lower() == "usuario" else col
                    valor = user.get(col, '')
                    st.markdown(f'<div class="dato-usuario"><strong>{etiqueta}:</strong> {valor}</div>', unsafe_allow_html=True)

            if user.get("Carpeta privada"):
                st.markdown(f"""
                <div style="margin-top: 10px;">
                    <a href="{user['Carpeta privada']}" target="_blank" style="text-decoration: none;">
                        <button style="background-color: var(--color-primary); color: white; border: none; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px;">
                            Abrir mi carpeta privada
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)

        # ===== SECCIÓN DE PROMOCIONES =====
        st.markdown('<div class="seccion">PROMOCIONES ACUMULADAS</div>', unsafe_allow_html=True)  # Eliminado el emoji
        
        def val(col): return int(user.get(col, 0)) if str(user.get(col)).replace('.', '').isdigit() else 0
        tappo = val(promo_tappo_col)
        bm1000 = val(promo_bm1000_col)
        tappo_2x1 = val(promo_tappo_2x1_col)
        total = tappo + bm1000 + tappo_2x1
        entregados = val("REPUESTOS") if "REPUESTOS" in df.columns else 0
        pendientes = val("PENDIENTE DE REPONER") if "PENDIENTE DE REPONER" in df.columns else 0

        # Nuevo diseño con columnas para mejor alineación
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="promo-card">
                <div class="promo-label">3x13 TAPPO</div>
                <div class="promo-value">{tappo}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="promo-card">
                <div class="promo-label">3×21 BM1000</div>
                <div class="promo-value">{bm1000}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="promo-card">
                <div class="promo-label">2+1 TAPPO</div>
                <div class="promo-value">{tappo_2x1}</div>
            </div>
            """, unsafe_allow_html=True)

        # Resumen de promociones con mejor espaciado
        st.markdown(f"""
        <div class="promo-total">
            <div style="margin-bottom: 8px;"><strong>Total promociones acumuladas:</strong> {total}</div>
            <div style="margin-bottom: 8px;"><strong>Promos entregadas:</strong> {entregados}</div>
            <div><strong>Pendientes de entregar:</strong> {pendientes}</div>
        </div>
        """, unsafe_allow_html=True)

        # ===== FORMULARIO PARA SUBIR PROMOCIONES =====
        with st.expander("SUBIR NUEVAS PROMOCIONES", expanded=False):  # Eliminado el emoji
            if "widget_key_promos" not in st.session_state:
                st.session_state.widget_key_promos = str(uuid.uuid4())
            if "widget_key_imgs" not in st.session_state:
                st.session_state.widget_key_imgs = str(uuid.uuid4())

            with st.container():
                promo1 = st.number_input("Promos 3x13 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_1")
                promo2 = st.number_input("Promos 3×21 BM1000", min_value=0, key=st.session_state.widget_key_promos + "_2")
                promo3 = st.number_input("Promos 2+1 TAPPO", min_value=0, key=st.session_state.widget_key_promos + "_3")
                imagenes = st.file_uploader("Sube los tickets o imágenes de comprobante", 
                                           type=["jpg", "png", "jpeg"], 
                                           accept_multiple_files=True, 
                                           key=st.session_state.widget_key_imgs)

                if st.button("SUBIR PROMOCIONES", key="subir_promos_btn"):  # Eliminado el emoji
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

        # ===== SECCIÓN COMBINADA: COMPENSACIONES Y VENTAS =====
        st.markdown('<div class="seccion">COMPENSACIONES & VENTAS</div>', unsafe_allow_html=True)  # Eliminado el emoji
        
        objetivo = str(user.get("OBJETIVO", "0")).strip()
        compensacion = str(user.get("COMPENSACION", "0")).strip()
        ventas_mensuales = str(user.get("VENTAS MENSUALES", "0")).strip()

        objetivo_num = to_float(objetivo)
        ventas_num = to_float(ventas_mensuales)

        porcentaje = (ventas_num / objetivo_num * 100) if objetivo_num > 0 else 0
        porcentaje = min(100, max(0, porcentaje))

        st.markdown(f"""
        <div class="sales-card">
            <div class="sales-label">VENTAS ACUMULADAS</div>
            <div class="sales-value">{ventas_num if ventas_num > 0 else "0"}</div>
            <div class="sales-target">Objetivo: {objetivo if objetivo_num > 0 else "No asignado"}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="dato-usuario">
            <strong>Compensación:</strong> {compensacion if compensacion else "No definido"}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" style="width: {porcentaje:.1f}%">{porcentaje:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ===== FORMULARIO DE REPORTE DE VENTAS =====
        with st.expander("REPORTAR VENTAS MENSUALES", expanded=False):  # Eliminado el emoji
            if "widget_key_ventas" not in st.session_state:
                st.session_state.widget_key_ventas = str(uuid.uuid4())
            if "widget_key_fotos" not in st.session_state:
                st.session_state.widget_key_fotos = str(uuid.uuid4())

            with st.form("formulario_ventas", clear_on_submit=True):
                cantidad = st.number_input("¿Cuántos dispositivos has vendido este mes?", 
                                         min_value=0, step=1, 
                                         key=st.session_state.widget_key_ventas + "_cantidad")
                fotos = st.file_uploader("Sube fotos como comprobante (tickets, vitrinas...)", 
                                        type=["jpg", "png"], 
                                        accept_multiple_files=True, 
                                        key=st.session_state.widget_key_fotos)
                enviar = st.form_submit_button("ENVIAR REPORTE")  # Eliminado el emoji

            if enviar:
                if not fotos:
                    st.warning("⚠️ Debes subir al menos una imagen como comprobante.")
                else:
                    try:
                        col_destino = "VENTAS MENSUALES"
                        row = df[df["Usuario"] == user["Usuario"]].index[0] + 2
                        col_index = df.columns.get_loc(col_destino) + 1
                        valor_anterior = user.get(col_destino, 0)
                        anterior = to_float(valor_anterior)
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

    # Botón de cerrar sesión en la parte inferior
    st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN", key="logout_btn"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # ===== PANTALLA DE LOGIN =====
    st.markdown('<div class="logo-container"><div class="logo-frame">', unsafe_allow_html=True)
    st.image("logo.png", use_container_width=True)  # Cambiado de use_column_width a use_container_width
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    if "recover_password" not in st.session_state:
        st.session_state.recover_password = False

    if not st.session_state.recover_password:
        with st.form("login_form"):
            st.markdown('<div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: 600; color: var(--color-primary);">INICIAR SESIÓN</div>', unsafe_allow_html=True)
            correo = st.text_input("Correo electrónico", key="login_email").strip().lower()
            clave = st.text_input("Contraseña", type="password", key="login_pass")
            submit = st.form_submit_button("ACCEDER", type="primary")

            st.markdown("""
            <div style="text-align: center; margin: 20px 0;">
                <a href="#" onclick="alert('Se enviará un enlace de recuperación a tu correo');" 
                   style="color: var(--color-primary); text-decoration: none; font-size: 14px;">
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
            st.markdown('<div style="text-align: center; margin-bottom: 20px; font-size: 18px; font-weight: 600; color: var(--color-primary);">RECUPERAR CONTRASEÑA</div>', unsafe_allow_html=True)
            recover_email = st.text_input("Ingresa tu correo electrónico", key="recover_email").strip().lower()
            submit_recover = st.form_submit_button("ENVIAR ENLACE")
            
            if submit_recover:
                user = buscar_usuario(recover_email)
                if user is not None:
                    st.success("Se ha enviado un enlace de recuperación a tu correo")
                    st.session_state.recover_password = False
                else:
                    st.error("Correo no encontrado")
