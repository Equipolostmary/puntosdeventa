import streamlit as st

# Verifica que el usuario esté logueado
if "email" not in st.session_state:
    st.warning("Debes iniciar sesión para acceder a esta sección.")
    st.stop()

st.set_page_config(page_title="Ventas", layout="centered")
st.title("📈 Registro de Ventas")

st.info("Desde aquí podrás consultar y registrar tus ventas mensuales.")

# Función que puedes reutilizar en otros archivos
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

# Este bloque se ejecuta siempre que se abre la página
st.success("✅ Página de ventas cargada correctamente.")
