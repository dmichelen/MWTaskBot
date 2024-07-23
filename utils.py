import requests
import json
from credentials import MONDAY_API_KEY, ULTRAMSG_INSTANCE_ID, ULTRAMSG_API_TOKEN

def fetch_monday_details(pulse_id, query):
    api_url = "https://api.monday.com/v2"
    headers = {"Authorization": MONDAY_API_KEY}

    data = {'query': query % pulse_id}
    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        if 'errors' in result:
            print(f"Errores en la respuesta de Monday.com: {result['errors']}")
        return result
    else:
        print(f"Error al obtener detalles de Monday.com: {response.status_code}")
        print(f"Respuesta de Monday.com: {response.text}")
        return None

def enviar_mensaje_whatsapp(destinatario, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    payload = {
        'token': ULTRAMSG_API_TOKEN,
        'to': destinatario,
        'body': mensaje
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Mensaje enviado correctamente")
    else:
        print(f"Error al enviar mensaje: {response.status_code}, {response.text}")

def obtener_destinatarios(assigned_to_names, contacts):
    destinatarios = [contacts[name.strip()] for name in assigned_to_names if name.strip() in contacts]
    return destinatarios
