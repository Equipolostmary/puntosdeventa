import streamlit as st

# Configuración de página
st.set_page_config(page_title="Ventas", layout="centered")

# Mostrar algo incluso si no hay login (para confirmar que carga)
st.title("📈 Página de ventas")
st.write("Esto es contenido de prueba para verificar que se muestra.")

# Verifica login (si quieres bloquear contenido real)
if "email" not in st.session_state:
    st.warning("Debes iniciar sesión para ver el contenido completo.")
    st.stop()

# Si hay login, continúa con la interfaz
st.success(f"¡Bienvenido {st.session_state['email']} a la zona de ventas!")

# Aquí puedes poner lo que quieras que cargue solo para usuarios autenticados
