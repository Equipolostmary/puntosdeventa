import streamlit as st

# Solo se muestra si hay sesión iniciada
if "email" not in st.session_state:
    st.warning("Debes iniciar sesión para acceder a esta sección.")
    st.stop()

st.set_page_config(page_title="Ventas", layout="centered")
st.title("📈 Registro de Ventas")

st.info("Desde aquí podrás consultar y actualizar tus ventas mensuales.")

# Función reutilizable para mostrar el panel de cada punto
def mostrar_panel(usuario, promociones, imagenes):
    st.subheader(f"Área privada de: {usuario.get('Nombre del punto de venta', 'Sin nombre')}")

    st.write("📈 Promociones actuales:", usuario.get("Nº Promos", 0))
    st.write("📁 Carpeta Drive asignada:", usuario.get("Carpeta Drive", "No asignada"))

    st.write("Número de promociones nuevas:", promociones)

    if imagenes:
        st.write("Imágenes seleccionadas:")
        for img in imagenes:
            st.image(img, width=200)
    else:
        st.info("Aún no se han seleccionado imágenes.")
