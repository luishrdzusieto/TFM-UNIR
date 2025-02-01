import os
import streamlit as st
from pymongo import MongoClient
from agentes_tareas_costos import verificar_cliente
from utils import generar_pdf
from predict import detectar_componentes

# Configuración de la página de Streamlit
st.set_page_config(page_title="Chatbot - Detección de Daños", page_icon="🚗", layout="centered")

# Cargar estilos desde el archivo CSS
with open("styles.css", "r") as css_file:
    st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

# Conexión a MongoDB Atlas
mongo_uri = "mongodb+srv://lhernand:Unir2025%24@cluster0.kw5ss.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client['aseguradora']
collection_costes = db['coste_reparaciones']

# Crear carpeta 'Historico fotos' si no existe
if not os.path.exists("Historico fotos"):
    os.makedirs("Historico fotos")

# Mapa entre los componentes detectados por YOLO y los nombres en la base de datos
mapa_clases = {
    'damaged door': 'Puerta',
    'damaged headlight': 'Faro',
    'damaged wind shield': 'Parabrisas',
    'damaged hood': 'Capó',
    'damaged bumper': 'Parachoques',
    'damaged window': 'Ventana',
    'damaged mirror': 'Espejo',
    'dent': 'Abolladura'
}

# Título del chatbot
st.markdown("<div class='title'>Chatbot para Detección de Daños en Coches 🚗</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Sube imágenes, detecta daños y genera informes fácilmente.</div>", unsafe_allow_html=True)

# Paso 0: Verificación de cliente
st.markdown("<div class='step-header'>🔍 Verificación de Cliente</div>", unsafe_allow_html=True)
nombre = st.text_input("Introduce tu nombre:")
apellido = st.text_input("Introduce tu apellido:")

if nombre and apellido:
    cliente = verificar_cliente(nombre, apellido)
    if cliente:
        st.success(f"¡Bienvenido {nombre} {apellido}!")

        # Paso 1: Selección de marca y modelo
        marca_cliente = cliente.get("marca_vehiculo", "")
        modelo_cliente = cliente.get("modelo_vehiculo", "")

        if marca_cliente and modelo_cliente:
            marca_seleccionada = st.selectbox("Marca asociada a tu coche", [marca_cliente])
            modelo_seleccionado = st.selectbox("Modelo asociado a tu coche", [modelo_cliente])

            if marca_seleccionada and modelo_seleccionado:
                st.write(f"Marca seleccionada: {marca_seleccionada}")
                st.write(f"Modelo seleccionado: {modelo_seleccionado}")

                # Paso 2: Subir imágenes del coche
                st.markdown("<div class='step-header'>📸 Subir Imágenes del Coche</div>", unsafe_allow_html=True)
                uploaded_files = st.file_uploader("Sube imágenes del coche (JPG/PNG):", accept_multiple_files=True)

                if uploaded_files:
                    all_detected_components = []

                    for idx, uploaded_file in enumerate(uploaded_files):
                        # Guardar y mostrar cada imagen
                        temp_file_name = f"imagen_temp_{idx}.jpg"
                        with open(temp_file_name, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.image(temp_file_name, caption=f"Imagen subida {idx+1}", use_column_width=True)

                        # Detectar componentes
                        st.info(f"Procesando la imagen {idx+1} para detectar componentes dañados...")
                        componentes_detectados = detectar_componentes(temp_file_name)

                        if componentes_detectados:
                            st.write(f"Componentes detectados: {componentes_detectados}")
                            all_detected_components.extend(componentes_detectados)

                    # Paso 3: Agregar daños manualmente
                    st.markdown("<div class='step-header'>🛠️ Agregar Daños Manualmente</div>", unsafe_allow_html=True)
                    piezas_disponibles = collection_costes.distinct("componente")
                    piezas_seleccionadas = st.multiselect("Selecciona piezas adicionales dañadas:", piezas_disponibles)

                    if piezas_seleccionadas:
                        all_detected_components.extend(piezas_seleccionadas)

                    # Paso 4: Calcular costos
                    if all_detected_components:
                        st.markdown("<div class='step-header'>💰 Calcular Costos</div>", unsafe_allow_html=True)
                        st.info("Calculando costos relacionados con los daños...")
                        componentes_unicos = list(set(all_detected_components))
                        costos = []

                        for componente in componentes_unicos:
                            nombre_componente = mapa_clases.get(componente, componente)
                            costo = collection_costes.find_one({
                                "marca_vehiculo": marca_seleccionada,
                                "modelo_vehiculo": modelo_seleccionado,
                                "componente": nombre_componente
                            })
                            if costo:
                                costos.append(costo)

                        if costos:
                            st.success("Costos calculados correctamente. Ahora puedes exportar el informe.")
                            st.write("Costos detectados:", costos)

                            # Generar y descargar informe
                            if st.button("Generar Informe en PDF"):
                                generar_pdf(cliente, costos, "imagen_temp_0.jpg", "informe_daños.pdf")
                                with open("informe_daños.pdf", "rb") as pdf_file:
                                    st.download_button(
                                        label="Descargar Informe PDF",
                                        data=pdf_file,
                                        file_name="informe_daños.pdf",
                                        mime="application/pdf",
                                    )
                        else:
                            st.error("No se encontraron costos relacionados con los daños detectados.")
    else:
        st.error("No estás registrado en nuestra base de datos. Por favor, contacta con soporte.")
