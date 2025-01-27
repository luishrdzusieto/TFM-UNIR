import streamlit as st
from agentes_tareas_costos import ejecutar_flujo
from predict import detectar_componentes

# Mapeo entre clases detectadas por YOLO y nombres en el CSV
mapa_clases = {
    'damaged door': 'Puerta',
    'damaged window': 'Ventana',
    'damaged headlight': 'Faro',
    'damaged mirror': 'Espejo',
    'dent': 'Abolladura',
    'damaged hood': 'Capó',
    'damaged bumper': 'Parachoques',
    'damaged wind shield': 'Parabrisas'
}

# Función para generar un informe claro y detallado
def generar_informe_claro(componentes):
    """
    Genera un informe más claro y estructurado.

    Args:
        componentes (list of dict): Lista con detalles del componente.

    Returns:
        str: Informe en formato de texto claro.
    """
    informe = ""
    for componente in componentes:
        informe += f"- Componente: {componente['Componente']}\n"
        informe += f"  - Coste del material: {componente['Coste_Material']} €\n"
        informe += f"  - Coste de la mano de obra: {componente['Coste_Mano_Obra']} €\n"
        informe += f"  - Coste total: {componente['Coste_Total']} €\n"
        informe += "\n"
    return informe

# Título del chatbot
st.title("Chatbot para detección de daños en coches 🚗")

# Paso 1: Pedir la marca del coche
marca = st.text_input("Introduce la marca de tu coche", placeholder="Ejemplo: Toyota")

if marca:
    st.write(f"¡Genial! Marca seleccionada: {marca}")

    # Paso 2: Subir la imagen del coche
    uploaded_file = st.file_uploader("Sube una imagen del coche (JPG/PNG)")

    if uploaded_file:
        # Guardar la imagen subida temporalmente
        with open("imagen_temp.jpg", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Mostrar la imagen previsualizada
        st.image("imagen_temp.jpg", caption="Imagen subida", use_column_width=True)

        # Detectar componentes con YOLO
        st.info("Procesando la imagen para detectar componentes dañados...")
        componentes_detectados = detectar_componentes("imagen_temp.jpg")

        if componentes_detectados:
            st.write("Componentes detectados por YOLO:", componentes_detectados)

            # Convertir las clases detectadas usando el mapeo
            componentes_convertidos = [mapa_clases.get(clase, clase) for clase in componentes_detectados]
            st.write("Componentes convertidos para el CSV:", componentes_convertidos)

            # Crear entradas simplificadas (solo el nombre del componente)
            entradas_detectadas = [{"Componente": comp} for comp in componentes_convertidos]
            st.write("Entradas generadas para el flujo:", entradas_detectadas)

            # Paso 3: Ejecutar flujo de costos
            st.info("Calculando costos y generando el informe...")
            componentes_encontrados = ejecutar_flujo(entradas_detectadas)

            if not componentes_encontrados:
                st.error("No se encontraron coincidencias en la base de datos con los componentes detectados.")
            else:
                # Generar el informe detallado
                informe_claro = generar_informe_claro(componentes_encontrados)
                st.text(informe_claro)
        else:
            st.warning("No se detectaron componentes en la imagen.")
