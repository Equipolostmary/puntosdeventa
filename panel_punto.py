import streamlit as st

def mostrar_panel(usuario, promociones, imagenes):
    st.subheader(f"Área privada de: {usuario['Nombre del punto de venta']}")

    st.write("📈 Promociones actuales:", usuario.get("Nº Promos", 0))
    st.write("📁 Carpeta Drive asignada:", usuario.get("Carpeta Drive", "No asignada"))

    st.write("Número de promociones nuevas:", promociones)

    if imagenes:
        st.write("Imágenes seleccionadas:")
        for img in imagenes:
            st.image(img, width=200)
    else:
        st.info("Aún no se han seleccionado imágenes.")