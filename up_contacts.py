import requests
import json
from credentials import MONDAY_API_KEY, BOARD_CONTACTS

def obtener_datos_tablero(api_key, board_id):
    url = "https://api.monday.com/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    query = """
    query GetBoardItems($board_id: [ID!]) {
        boards(ids: $board_id) {
            items_page {
                items {
                    id
                    name
                    column_values {
                        id
                        value
                    }
                }
            }
        }
    }
    """
    variables = {
        "board_id": [board_id]  # Usar board_id como cadena
    }
    data = {
        "query": query,
        "variables": variables
    }
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        return response_json
    else:
        raise Exception(f"Error al hacer la solicitud: {response.status_code}, {response.text}")

def actualizar_contacts(datos):
    contactos = {}
    boards = datos.get('data', {}).get('boards', [])
    print(boards)

    if not boards:
        print("No se encontraron tableros. Verifica el ID del tablero y los datos en Monday.com.")
        return

    for board in boards:
        items_page = board.get('items_page', {})
        items = items_page.get('items', [])
        for item in items:
            name = item.get('name', '')
            phone = None
            es_persona = False
            for column in item.get('column_values', []):
                if column['id'] == 'phone__1':
                    phone_value = column.get('value')
                    if phone_value:
                        phone_dict = json.loads(phone_value)
                        phone = phone_dict.get('phone')
                        if column['id'] == 'status2__1':
                            status_value = column.get('value')
                            if status_value:
                                status_dict = json.loads(status_value)
                                es_persona = status_dict.get('text') == 'Persona'

            if phone:
                if es_persona:
                    contactos[name] = '+1' + phone
                else:
                    contactos[name] = phone
    
    with open("contacts.py", "w") as f:
        f.write("# contacts.py\n\n")
        f.write("contacts = {\n")
        for name, phone in contactos.items():
            f.write(f'    "{name}": "{phone}",\n')
        f.write("}\n")

def ejecutar_actualizacion_contactos():
    # Ejemplo de uso
    board_id = BOARD_CONTACTS  # Leer el ID del tablero desde credentials.py
    try:
        datos_tablero = obtener_datos_tablero(MONDAY_API_KEY, board_id)
        actualizar_contacts(datos_tablero)
        print("El archivo contacts.py ha sido actualizado.")
    except Exception as e:
        print(e)

ejecutar_actualizacion_contactos()
