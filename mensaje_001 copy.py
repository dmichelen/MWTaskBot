import requests
import calendar
from datetime import datetime
from credentials import ULTRAMSG_INSTANCE_ID, ULTRAMSG_API_TOKEN
from contacts import contacts

# Configuración de UltraMsg
url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
API_TOKEN = ULTRAMSG_API_TOKEN

def send_whatsapp_message(to, message):
    data = {
        "token": API_TOKEN,
        "to": to,
        "body": message
    }
    response = requests.post(url, data=data)
    print(response.json())

def create_message():
    message = """
    Saludos,

    Estimados, se les recuerda que las facturas deben estar en nuestras instalaciones antes del día ‼30 del mes en curso‼ para poder brindarles un excelente servicio, como hasta ahora nos ha caracterizado.

    🔹Se solicita enviar el recibo Entregado por la Parada 🔢por privado a los números 849-816-8104 o 849-816-8132 para su retiro. En el paquete en la informacion debe colocarse el número de teléfono principal, 809-541-2840, a nombre de PSS ODONTODOM, ya que se han presentado inconvenientes con estos en las diferentes paradas.

    🔸Los soportes radiográficos, fotos y periodontogramas de Humano Seguro y Primera deben ser enviados al correo soporteradiografico@odontodom.net, utilizando la plantilla correspondiente. Para cualquier inquietud o aclaración, estamos a su disposición.

    Odontodom-Automatizado
    """
    return message

def is_sunday(date):
    return date.weekday() == 6

def verificar_y_enviar_mensaje():
    # Lista de destinatarios
    recipients = contacts["Demian Michelen"]
    
    # Crear mensaje
    mensaje = create_message()
    
    # Verificar la fecha actual
    today = datetime.now()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    
    # Verificar si la fecha está entre el 20 y el último día del mes
    if 20 <= today.day <= last_day_of_month and today.weekday() != 6:  # Excluye domingos
        for recipient in recipients:
            send_whatsapp_message(recipient, mensaje)
        return True
    else:
        return False
