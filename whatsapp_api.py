# Archivo whatsapp_api.py

import requests
from credentials import ULTRAMSG_INSTANCE_ID, ULTRAMSG_API_TOKEN

def enviar_mensaje_whatsapp(destinatario, mensaje):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_API_TOKEN,
        "to": destinatario,
        "body": mensaje
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Mensaje enviado a {destinatario}")
    else:
        print(f"Error al enviar mensaje a {destinatario}: {response.text}")
