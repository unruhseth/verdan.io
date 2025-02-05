import requests
from flask import current_app

def soracom_request(method, endpoint, data=None):
    """Helper function to send authenticated requests to Soracom API"""
    headers = {
        "X-Soracom-API-Key": current_app.config["SORACOM_API_KEY"],
        "X-Soracom-Token": current_app.config["SORACOM_TOKEN"],
        "Content-Type": "application/json"
    }
    url = f"{current_app.config['SORACOM_BASE_URL']}{endpoint}"

    response = requests.request(method, url, headers=headers, json=data)
    
    if response.status_code >= 400:
        return {"error": response.json()}, response.status_code

    return response.json()
