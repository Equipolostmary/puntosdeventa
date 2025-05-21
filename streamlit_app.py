from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from drive_upload import conectar_drive, subir_archivo_a_drive

if st.button("Subir promociones"):
    if not imagenes:
        st.warning("Debes seleccionar al menos una imagen.")
    else:
        # 📂 Conectar a Drive y subir imágenes a la carpeta privada
        service = conectar_drive("service_account.json")
        carpeta_id = punto["Carpeta privada"]

        for imagen in imagenes:
            subir_archivo_a_drive(service, imagen, imagen.name, carpeta_id)

        # 📄 Conectar a Google Sheets para actualizar columnas L y M
        SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPE)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(SHEET_URL)
        worksheet = sheet.worksheet(PESTAÑA)

        # 🔍 Buscar la fila del punto de venta por correo
        correos = worksheet.col_values(3)  # columna C = correo electrónico
        fila_usuario = next((i + 1 for i, val in enumerate(correos) if val.strip().lower() == correo), None)

        if fila_usuario:
            # Leer y actualizar columna L (promos acumuladas) y M (fecha)
            valor_actual = worksheet.cell(fila_usuario, 12).value  # columna L
            total_actual = int(valor_actual) if valor_actual.isnumeric() else 0
            nuevo_total = total_actual + promociones

            worksheet.update_cell(fila_usuario, 12, str(nuevo_total))  # columna L
            worksheet.update_cell(fila_usuario, 13, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # columna M

            st.success(f"✅ Se subieron {len(imagenes)} imagen(es) y se actualizaron tus promociones.")
            st.write("📦 Promociones acumuladas:", nuevo_total)
        else:
            st.error("No se pudo localizar tu fila en el Excel.")
