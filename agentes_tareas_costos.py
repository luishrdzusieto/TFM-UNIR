import csv

def ejecutar_flujo(entradas):
    """
    Busca información relevante en el CSV basado en las entradas proporcionadas.

    Args:
        entradas (list of dict): Lista de diccionarios con 'Componente'.

    Returns:
        list of dict: Información detallada de los componentes encontrados.
    """
    contenido = []
    with open('./dataset_piezas.csv', mode='r', encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file, delimiter=';')
        for entrada in entradas:
            for row in reader:
                if row['Componente'] == entrada['Componente']:
                    row['Coste_Total'] = int(row['Coste_Material']) + int(row['Coste_Mano_Obra'])
                    contenido.append(row)
            file.seek(0)  # Reinicia la lectura del archivo
    return contenido
