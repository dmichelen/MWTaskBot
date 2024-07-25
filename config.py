import json
from datetime import datetime

# Diccionario para la traducción manual de los días de la semana
DAYS_TRANSLATION = {
    'Sunday': 'Domingo',
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes',
    'Saturday': 'Sábado'
}

# Consultas GraphQL
queries = {
    "default": """
    query {
        items (ids: [%s]) {
            id
            name
            column_values {
                id
                text
                value
            }
        }
    }
    """,
    "specific_query_1": """
    query {
        items (ids: [%s]) {
            id
            name
            column_values {
                id
                text
                value
            }
        }
    }
    """,
    # Agrega aquí más consultas según sea necesario.
}

# Diccionario de configuraciones de solicitudes y plantillas de mensajes
requests_config = {
    # Configuración para la ruta /reunion1 - Este es al momento de crear una reunion
    "reunion1_config_key": {
        "query": queries["specific_query_1"],
        "message_template": """
        🗓 *¡Nueva Reunión Creada!* 🗓 
        
        *📌 Motivo:* {pulse_name}
        
        *📅 Día:* {fecha_prop} *({nombre_dia})*
        
        *🕒 Hora:* {hora_prop}
        
        *⌛ Duración:* {duracion}

        *📍 Lugar:* {lugar}
        
        *👥 Participantes:* {assigned_to}
        """,
        "custom_extract_function": "extract_assigned_to_names"
    },
    # Configuración para la ruta /reunion2 - Esto es para recordatorios de reuniones
    "reunion2_config_key": {
        "query": queries["specific_query_1"],
        "message_template": """
        🗓 *¡Recordatorio Reunion Agendada!* 🗓 
        
        *📌 Motivo:* {pulse_name}
        
        *📅 Día:* {fecha_prop} *({nombre_dia})*
        
        *🕒 Hora:* {hora_prop}

        *⌛ Duración:* {duracion}

        *📍 Lugar:* {lugar}

        🔔 Se llevará a cabo *{dia_restante}*
        
        *👥 Participantes:* {assigned_to}
        """,
        "custom_extract_function": "extract_assigned_to_names"
    },
    # Otras configuraciones...
}

# Función para extraer los nombres de las personas asignadas y de la columna men_desplegable0__1
def extract_assigned_to_names(column_details):
    assigned_to_names = set()
    for col in column_details:
        if col['id'] == 'person':
            # Extraer los nombres de las personas asignadas
            if isinstance(col['value'], str):
                col_value = json.loads(col['value'])
            else:
                col_value = col['value']

            assigned_to_names.add(col.get('text', 'N/A'))
        elif col['id'] == 'men__desplegable0__1':
            # Extraer los nombres de la columna men_desplegable0__1
            if col['text']:
                names = [name.strip() for name in col['text'].split(',')]
                assigned_to_names.update(names)
                print(names)
    return ', '.join(assigned_to_names)

# Función para generar el mensaje utilizando los datos y la plantilla proporcionada
def generar_mensaje(data, config):
    if config is None:
        print("No se encontró una configuración específica para los datos recibidos.")
        return None

    pulse_name = data.get('pulseName', 'N/A')
    group_name = data.get('groupName', 'N/A')
    pulse_id = data.get('pulseId', 'N/A')
    dia_restante = data.get('valor_data', 'N/A')

    details = data.get('details', {}).get('data', {}).get('items', [{}])
    if not details:
        print("No se encontraron detalles de items en los datos proporcionados.")
        return None
    details = details[0]

    task_name = details.get('name', 'N/A')
    column_details = details.get('column_values', [])

    column_info = ', '.join([f"{col['id']}: {col['text'] or 'N/A'}" for col in column_details])

    # Utilizar la función personalizada para extraer nombres de asignados
    extract_function = globals()[config["custom_extract_function"]]
    assigned_to = extract_function(column_details)

    # Extraer la fecha de la columna 'fecha__1' y convertirla al día de la semana
    fecha_prop = 'N/A'
    nombre_dia = 'N/A'
    for col in column_details:
        if col['id'] == 'fecha__1':
            fecha_prop = col.get('text', 'N/A')
            if fecha_prop != 'N/A':
                try:
                    fecha_obj = datetime.strptime(fecha_prop, '%Y-%m-%d')
                    nombre_dia = fecha_obj.strftime('%A')  # Obtener el nombre del día en español
                    # Traducir manualmente si es necesario
                    nombre_dia = DAYS_TRANSLATION.get(nombre_dia, nombre_dia)
                except ValueError:
                    nombre_dia = 'Fecha Inválida'
            break

    # Extraer la hora de la columna 'hora__1'
    hora_prop = 'Pendiente'
    for col in column_details:
        if col['id'] == 'hora__1':
            hora_prop = col.get('text', 'Pendiente')
            if not hora_prop:
                hora_prop = 'Pendiente'
            break

    # Extraer la duración de la columna 'dropdown6__1'
    duracion = 'N/A'
    for col in column_details:
        if col['id'] == 'dropdown6__1':
            duracion = col.get('text', 'N/A')
            break

    # Extraer el lugar de la columna 'dropdown__1'
    lugar = 'N/A'
    for col in column_details:
        if col['id'] == 'dropdown__1':
            lugar = col.get('text', 'N/A')
            break

    # Generar el mensaje usando la plantilla y los datos extraídos
    mensaje = config["message_template"].format(
        pulse_name=pulse_name,
        group_name=group_name,
        task_name=task_name,
        column_info=column_info,
        assigned_to=assigned_to,
        pulse_id=pulse_id,
        fecha_prop=fecha_prop,  # Añadir la fecha al mensaje
        nombre_dia=nombre_dia,  # Añadir el nombre del día al mensaje
        hora_prop=hora_prop,    # Añadir la hora al mensaje
        dia_restante=dia_restante,   # Añadir el texto de 'Es:' al mensaje
        duracion=duracion,       # Añadir la duración al mensaje
        lugar=lugar             # Añadir el lugar al mensaje
    )

    return mensaje, assigned_to.split(', ')
