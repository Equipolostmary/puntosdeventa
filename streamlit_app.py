import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Lost Mary Estanco Club", page_icon=":purple_heart:", layout="wide")

# Correo del administrador autorizado
ADMIN_EMAIL = "equipolostmary@gmail.com"

# Estilos globales (fondo degradado morado, ocultar/mostrar menús, resaltar campo de correo)
page_style = """
<style>
/* Fondo morado degradado para la página principal */
[data-testid="stAppViewContainer"] > .main {
    background: linear-gradient(to bottom right, #b5179e, #7209b7);
}
/* Hacer transparente el encabezado predeterminado de Streamlit (para ver el fondo) */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
/* Resaltar campos de texto (especialmente el de correo electrónico) */
input[type="text"], input[type="password"] {
    border: 2px solid white;
    background-color: rgba(255,255,255,0.8);
    color: black;
    box-shadow: 0 0 10px 2px rgba(255,255,255,0.5);
}
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# Ocultar menú y pie de página de Streamlit para usuarios no administradores
if st.session_state.get("email") != ADMIN_EMAIL:
    hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

# Inicializar estado de sesión para el correo del usuario
if "email" not in st.session_state:
    st.session_state.email = None

# Pantalla de inicio de sesión
if st.session_state.email is None:
    # Mostrar logo centrado en la pantalla de login
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", use_column_width=True)  # Asegúrate de tener "logo.png" en el directorio
    st.subheader("Iniciar sesión")
    email_input = st.text_input("Correo electrónico:", placeholder="Introduce tu correo")
    login_button = st.button("Acceder")
    if login_button:
        if email_input.strip() == "":
            st.error("Por favor, ingresa un correo válido.")
        else:
            # Guardar el correo en el estado de sesión y recargar la app
            st.session_state.email = email_input.strip().lower()
            st.experimental_rerun()

# Zona privada (después de iniciar sesión)
else:
    user_email = st.session_state.email
    if user_email == ADMIN_EMAIL:
        # Usuario administrador: mostrar funcionalidad completa
        # Asegurar que el menú y pie de página predeterminados de Streamlit sean visibles para el admin
        st.markdown(
            "<style>#MainMenu {visibility: visible !important;} footer {visibility: visible !important;}</style>",
            unsafe_allow_html=True
        )
        # Encabezado con logo centrado
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.image("logo.png", use_column_width=True)
        # Menú de navegación superior (tabs) para el admin
        tab1, tab2 = st.tabs(["Zona privada", "Gestión de la app"])
        with tab1:
            st.subheader(f"Bienvenido a tu zona privada, **{user_email}**.")
            st.write("Aquí puedes ver tu información personal y contenido exclusivo para miembros.")
            # ... (contenido privado del usuario administrador)
        with tab2:
            st.subheader("Gestión de la aplicación")
            st.write("Opciones avanzadas de administración de la app:")
            st.write("- **Gestión de usuarios**: agregar/eliminar usuarios, restablecer contraseñas, etc.")
            st.write("- **Gestión de contenidos**: crear o editar promociones, actualizaciones, etc.")
            st.write("- **Otras configuraciones**: ajustes generales de la aplicación.")
        # Pie de página personalizado para el admin (opcional)
        st.markdown(
            "<hr/><p style='text-align:center; font-size:0.8em;'>© 2025 Lost Mary Estanco Club — Panel de Administración</p>",
            unsafe_allow_html=True
        )
    else:
        # Usuario normal: mostrar solo su zona privada (funcionalidad restringida)
        st.subheader(f"Bienvenido a tu zona privada, **{user_email}**.")
        st.write("Aquí puedes ver tu información personal y contenido exclusivo para miembros.")
        # ... (contenido privado del usuario sin opciones avanzadas)
