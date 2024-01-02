# utils.py
import psutil
from datetime import datetime
import requests

def get_logged_in_users():
    users_info = []
    # Iterate through all logged-in users
    for user in psutil.users():
        timestamp = datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M:%S")
        ip_address = user.host
        # Get additional location information using GeoIP
        location_info = get_location_info(ip_address) if ip_address else None
        users_info.append({
            "timestamp": timestamp,
            "ip_address": ip_address,
            "location_info": location_info
        })
    return users_info

def get_location_info(ip_address):
    try:
        # Use a geoip service to get location information based on IP
        response = requests.get(f"https://ipinfo.io/{ip_address}/json")
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching location information for {ip_address}: {e}")
        return None
