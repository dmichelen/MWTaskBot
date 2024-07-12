# Archivo monday_api.py

import requests
from credentials import MONDAY_API_URL, MONDAY_API_KEY

def fetch_monday_details(pulse_id, query):
    headers = {
        "Authorization": MONDAY_API_KEY,
        "Content-Type": "application/json"
    }
    response = requests.post(MONDAY_API_URL, json={'query': query % pulse_id}, headers=headers)
    
    if response.status_code != 200:
        print(f"Error al obtener datos de Monday.com: {response.text}")
        return None
    
    return response.json()
