import streamlit as st
import pandas as pd

try:
    from google.oauth2 import service_account
    import gspread
    # Autenticación con Google Sheets mediante una cuenta de servicio
    scopes = ["https://www.googleapis.com/auth/spreadsheets", 
              "https://www.googleapis.com/auth/drive"]
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(creds)
    # Abrir la hoja de cálculo de Google Sheets por su ID
    spreadsheet = client.open_by_key(st.secrets["sheet_id"])
    worksheet = spreadsheet.sheet1  # O usar .worksheet("NombreHoja") si no es la primera
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Error cargando datos desde Google Sheet: {e}")
    st.stop()

# Configuración de la página y estilo (fondo morado claro y fuente Montserrat)
st.set_page_config(page_title="Puntos de Venta", page_icon="📊", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    [data-testid="stAppViewContainer"] > .main {
        background-color: #E9D5FF;
    }
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# Mostrar el logo centrado (asegúrate de tener un archivo 'logo.png' en el directorio de la app)
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.write("")  # Columna vacía para centrar
with col2:
    st.image("logo.png", use_column_width=True)
with col3:
    st.write("")

st.title("Acceso a Puntos de Venta")

# Función auxiliar para encontrar la fila de un usuario por correo electrónico
def encontrar_usuario_por_correo(email):
    email = email.strip().lower()
    # Buscar en la primera columna del DataFrame
    mask = df[df.columns[0]].astype(str).str.lower() == email
    if mask.any():
        return mask
    # Si no está en la primera columna, buscar en columnas posibles de correo
    posibles = ["email", "correo", "correo electrónico", "correo electronico"]
    for col in df.columns:
        if str(col).lower() in posibles:
            mask = df[col].astype(str).str.lower() == email
            if mask.any():
                return mask
    # Si no se encontró en ninguna columna, devolver máscara vacía
    return mask  # (serie booleana de False)

# Inicializar estado de autenticación en la sesión
if "auth_email" not in st.session_state:
    st.session_state.auth_email = None

# Si el usuario ya está autenticado, mostrar su panel; si no, mostrar formulario de login
if st.session_state.auth_email:
    # Usuario autenticado: obtener sus datos
    user_email = st.session_state.auth_email
    mask = encontrar_usuario_por_correo(user_email)
    if not mask.any():
        # Si el correo ya no existe en la hoja (por ejemplo, fue eliminado)
        st.warning("Usuario no encontrado. Por favor, inicia sesión de nuevo.")
        st.session_state.auth_email = None
        st.experimental_rerun()
    datos_usuario = df[mask].iloc[0]
    admin_email = "equipolostmary@gmail.com"
    if user_email == admin_email:
        # Panel de administrador
        st.success("Bienvenido, administrador.")
        st.subheader("Resumen de todos los puntos")
        df_display = df.copy()
        # Ocultar columna de contraseña si existe
        password_cols = [c for c in df_display.columns if str(c).lower() in ["contraseña", "contrasena", "password"]]
        if password_cols:
            df_display.drop(password_cols, axis=1, inplace=True)
        st.dataframe(df_display)
    else:
        # Panel de un usuario normal
        # Saludo con el nombre si está disponible
        nombre = None
        for col in datos_usuario.index:
            if str(col).lower() in ["nombre", "name"]:
                nombre = datos_usuario[col]
                break
        if nombre:
            st.success(f"Bienvenido, {nombre}!")
        else:
            st.success("Bienvenido!")
        # Mostrar datos personales (excepto contraseña y correo)
        st.subheader("Tus datos personales")
        for col, val in datos_usuario.items():
            col_lower = str(col).lower()
            if col_lower in ["contraseña", "contrasena", "password", "correo", "correo electrónico", "correo electronico", "email"]:
                continue  # Saltar contraseña y correo
            st.write(f"**{col}:** {val}")
        # Mostrar información de promociones
        st.subheader("Estado de tus promociones")
        entregados_tappo = entregados_bm1000 = None
        falta_tappo = falta_bm1000 = None
        total_tappo = total_bm1000 = None
        # Extraer contadores y valores de promociones TAPPO y BM1000
        for col, val in datos_usuario.items():
            col_lower = str(col).lower()
            if "tappo" in col_lower and "entregado" in col_lower:
                entregados_tappo = val
            elif "bm1000" in col_lower and "entregado" in col_lower:
                entregados_bm1000 = val
            elif "tappo" in col_lower and ("falta" in col_lower or "pendiente" in col_lower):
                falta_tappo = val
            elif "bm1000" in col_lower and ("falta" in col_lower or "pendiente" in col_lower):
                falta_bm1000 = val
            elif "tappo" in col_lower and ("promo" in col_lower or "total" in col_lower) and total_tappo is None:
                total_tappo = val
            elif "bm1000" in col_lower and ("promo" in col_lower or "total" in col_lower) and total_bm1000 is None:
                total_bm1000 = val
        # Mostrar totales asignados de promociones (si existen)
        if total_tappo is not None:
            st.write(f"**Promoción TAPPO asignada:** {total_tappo}")
        if total_bm1000 is not None:
            st.write(f"**Promoción BM1000 asignada:** {total_bm1000}")
        # Mostrar entregados y faltantes con texto destacado
        if entregados_tappo is not None:
            st.markdown(f"**📦 TAPPO entregados: {entregados_tappo}**")
        if falta_tappo is not None:
            st.markdown(f"**📦 TAPPO por entregar: {falta_tappo}**")
        if entregados_bm1000 is not None:
            st.markdown(f"**📦 BM1000 entregados: {entregados_bm1000}**")
        if falta_bm1000 is not None:
            st.markdown(f"**📦 BM1000 por entregar: {falta_bm1000}**")
else:
    # Formulario de inicio de sesión
    correo = st.text_input("Correo electrónico:")
    login_btn = st.button("Acceder")
    if login_btn:
        if correo.strip() == "":
            st.warning("Por favor, introduce un correo electrónico.")
        else:
            mask = encontrar_usuario_por_correo(correo)
            if not mask.any():
                st.error("Correo no registrado. Por favor, verifica el email o contacta soporte.")
            else:
                # Autenticación exitosa: guardar email en la sesión y recargar la interfaz
                st.session_state.auth_email = correo.strip().lower()
                st.experimental_rerun()
