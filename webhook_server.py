# webhook_server.py

from flask import Flask, request, jsonify
from utils import fetch_monday_details, enviar_mensaje_whatsapp, 
from config import requests_config, generar_mensaje
from up_contacts import ejecutar_actualizacion_contactos  # Importar la función para actualizar contactos
from contacts import contacts  # Importar contactos desde contacts.py
from credentials import HOST_SERVIDOR, PORT_NUMBER

app = Flask(__name__) 
# Almacenamiento temporal para los datos del webhook y los detalles adicionales
data_store = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    datos1 = request.json

    # Manejo del desafío de Monday.com
    if 'challenge' in datos1:
        return jsonify({'challenge': datos1['challenge']}), 200

    # Imprimir los datos recibidos por el webhook
    print("Datos recibidos por el webhook:")
    print(datos1)

    pulse_id = datos1.get('event', {}).get('pulseId', 'N/A')
    board_id = str(datos1.get('event', {}).get('boardId', 'N/A'))
    group_id = datos1.get('event', {}).get('groupId', 'N/A')
    event_type = datos1.get('event', {}).get('type', 'N/A')
    column_id = datos1.get('event', {}).get('columnId', 'N/A')
    column_title = datos1.get('event', {}).get('columnTitle', 'N/A')
    valor_data = datos1.get('event', {}).get('value', {}).get('label', {}).get('text', 'N/A')

    # Imprimir los valores de board_id, group_id, event_type, column_id, column_title
    print("Valores recibidos:")
    print(f"board_id: {board_id}, group_id: {group_id}, event_type: {event_type}, column_id: {column_id}, column_title: {column_title}, valor_data: {valor_data}")

    if pulse_id == 'N/A':
        return jsonify({"error": "Pulse ID not provided"}), 400

    # Almacenar los datos del webhook en data_store
    data_store[pulse_id] = {
        "app": datos1.get('event', {}).get('app', 'N/A'),
        "type": event_type,
        "triggerTime": datos1.get('event', {}).get('triggerTime', 'N/A'),
        "subscriptionId": datos1.get('event', {}).get('subscriptionId', 'N/A'),
        "userId": datos1.get('event', {}).get('userId', 'N/A'),
        "boardId": board_id,
        "pulseId": pulse_id,
        "pulseName": datos1.get('event', {}).get('pulseName', 'N/A'),
        "groupId": group_id,
        "groupName": datos1.get('event', {}).get('groupName', 'N/A'),
        "groupColor": datos1.get('event', {}).get('groupColor', 'N/A'),
        "isTopGroup": datos1.get('event', {}).get('isTopGroup', 'N/A'),
        "columnValues": datos1.get('event', {}).get('columnValues', 'N/A'),
        "triggerUuid": datos1.get('event', {}).get('triggerUuid', 'N/A'),
        "columnTitle": column_title,
        "valor_data": valor_data,
    }

    # Construir las claves para buscar en requests_config
    config_key_specific = f"{board_id}.{group_id}.{event_type}.columnId_{column_id}.pulseId_{pulse_id}"
    config_key_column_title = f"{board_id}.{group_id}.{event_type}.columnId_{column_id}.columnTitle_{column_title}"
    config_key_general = f"{board_id}.{group_id}.{event_type}.columnId_{column_id}"
    config_key_less_specific = f"{board_id}.{event_type}.columnId_{column_id}"

    # Determinar la configuración de la solicitud y la plantilla del mensaje
    config = requests_config.get(
        config_key_specific,
        requests_config.get(
            config_key_column_title,
            requests_config.get(
                config_key_general,
                requests_config.get(config_key_less_specific, None)
            )
        )
    )

    # Verificar qué configuración se está utilizando
    if config is None:
        print("No se encontró una configuración específica para los datos recibidos. No se enviará un mensaje de WhatsApp.")
        return jsonify({"status": "No configuration found"}), 200
    elif config == requests_config.get(config_key_specific):
        print("Usando configuración específica con Pulse ID")
    elif config == requests_config.get(config_key_general):
        print("Usando configuración específica general")
    elif config == requests_config.get(config_key_column_title):
        print("Usando configuración específica con Column Title")
    else:
        print("Usando configuración menos específica")

    # Imprimir la consulta que se enviará a Monday.com
    query = config["query"]
    print("Consulta enviada a Monday.com:")
    print(query % pulse_id)

    # Hacer una petición a Monday.com para obtener más detalles de la tarea
    datos2 = fetch_monday_details(pulse_id, query)
    if not datos2:
        return jsonify({"error": "Failed to fetch data from Monday.com"}), 500

    # Imprimir los datos recibidos del request a Monday.com
    print("Datos recibidos de Monday.com:")
    print(datos2)

    # Almacenar los detalles adicionales obtenidos de Monday.com
    data_store[pulse_id]["details"] = datos2

    # Llamar a la función para actualizar contactos
    ejecutar_actualizacion_contactos()

    # Generar el mensaje para enviar por WhatsApp y obtener los nombres asignados
    mensaje, assigned_to_names = generar_mensaje(data_store[pulse_id], config)
    if mensaje is None:
        return jsonify({"status": "Message generation failed"}), 200

    # Obtener los números de teléfono de los destinatarios
    destinatarios = obtener_destinatarios(assigned_to_names, contacts)

    # Imprimir los datos que se enviarán a UltraMsg
    print("Datos enviados a UltraMsg:")
    print("Destinatarios:", destinatarios)
    print("Mensaje:", mensaje)

    # Enviar el mensaje a cada destinatario
    for destinatario in destinatarios:
        enviar_mensaje_whatsapp(destinatario, mensaje)
    
    return jsonify({"status": "Message sent"}), 200

@app.route('/mmsg', methods=['POST'])
def mmsg():
    datosmmsg = request.json

    # Manejo del desafío de Monday.com
    if 'challenge' in datosmmsg:
        return jsonify({'challenge': datosmmsg['challenge']}), 200
    
    print(datosmmsg)
    return jsonify({"status": "Message sent"}), 200


if __name__ == '__main__':
    # Enviar mensaje al iniciar el servidor
    destinatario = contacts["Demian Michelen"]
    mensaje = "El servidor acaba de encender. Todo listo para el funcionamiento."
    enviar_mensaje_whatsapp(destinatario, mensaje)
    app.run(host= HOST_SERVIDOR, port=PORT_NUMBER)

    