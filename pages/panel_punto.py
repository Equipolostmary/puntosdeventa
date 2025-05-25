import streamlit as st

def mostrar_panel(usuario, promociones, imagenes):
    st.subheader(f"Área privada de: {usuario.get('Expendiduría', 'Punto sin nombre')}")

    st.markdown("### 📋 Datos del punto de venta")
    st.markdown(f"- **Dirección:** {usuario.get('Dirección', 'Sin datos')}")
    st.markdown(f"- **Provincia:** {usuario.get('Provincia', 'Sin datos')}")
    st.markdown(f"- **Teléfono:** {usuario.get('Teléfono', 'Sin datos')}")
    st.markdown(f"- **Correo:** {usuario.get('Dirección de correo electrónico', 'Sin datos')}")
    st.markdown(f"- **ID Carpeta Drive:** {usuario.get('Carpeta privada', 'Sin datos')}")

    st.markdown("---")
    st.markdown("### 📦 Estado de promociones")
    st.markdown(f"- **Promoción 2+1 TAPPO:** {usuario.get('Promoción 2+1 TAPPO', 0)}")
    st.markdown(f"- **Entregados TAPPO:** {usuario.get('Entregados promo TAPPO', 0)}")
    st.markdown(f"- **Faltan TAPPO:** {usuario.get('Falta por entregar TAPPO', 0)}")
    st.markdown(f"- **Promoción 3×21 BM1000:** {usuario.get('Promoción 3×21 BM1000', 0)}")
    st.markdown(f"- **Entregados BM1000:** {usuario.get('Entregados promo BM1000', 0)}")
    st.markdown(f"- **Faltan BM1000:** {usuario.get('Falta por entregar BM1000', 0)}")

    st.markdown(f"- 📆 **Última actualización:** {usuario.get('Ultima actualización', 'No registrada')}")

    st.markdown("---")
    st.markdown("### 🖼️ Imágenes subidas")

    if imagenes:
        for img in imagenes:
            st.image(img, width=300)
    else:
        st.info("Este punto aún no ha subido imágenes.")
