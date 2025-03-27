import win32com.client
from pynput import keyboard
import time
import requests
import socket
import json
import ipaddress
import subprocess
import re
import threading

def get_temporary_ipv6():
    """Get temporary IPv6 address on Windows"""
    try:
        result = subprocess.check_output(['ipconfig', '/all'], text=True, encoding='utf-8')
        for line in result.splitlines():
            if "Temporary IPv6 Address" in line:
                match = re.search(r"Temporary IPv6 Address[ .]*: ([a-fA-F0-9:]+)", line)
                if match:
                    ip_address = match.group(1).strip()
                    try:
                        ipaddress.IPv6Address(ip_address)
                        return ip_address
                    except ipaddress.AddressValueError:
                        continue
        return None
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error getting IPv6: {e}")
        return None

def check_scanner_connected():
    wmi = win32com.client.GetObject("winmgmts:")
    devices = wmi.InstancesOf("Win32_PnPEntity")
    for device in devices:
        if device.PNPDeviceID and "HID" in device.PNPDeviceID:  
            print(f"Connected device: {device.Name} (PNPDeviceID: {device.PNPDeviceID})")
            return True
    return False
def get_system_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error retrieving system IP: {e}")
        return None

def send_barcode_via_http(barcode_data):
    system_ip = get_system_ip()
    system_ipv6_temp = get_temporary_ipv6()
    if not system_ip:
        print("Could not retrieve system IP. Using default IP.")
        system_ip = "192.168.1.4"  
    url = f"http://{system_ip}:8000/get_backend_data_scanned_data/"
    payload = {"qr_data": barcode_data,"system_ip":system_ip,"system_ipv6_temp":system_ipv6_temp}
    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("***************************************************")
            print(f"Barcode data sent successfully: {barcode_data}")
            print("***************************************************")
        else:
            print(f"Failed to send barcode data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending barcode data: {e}")


def capture_barcode_data():
    barcode_data = ""
    def on_press(key):
        nonlocal barcode_data
        try:
            barcode_data += key.char
        except AttributeError:
            if key == keyboard.Key.enter:
                print(f"Barcode Scanned: {barcode_data}")
                send_barcode_via_http(barcode_data)
                barcode_data = ""  # Reset for the next scan
                return False  # Stop the listener
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    while True:  
        if check_scanner_connected():
            print("Helett HT20 Barcode Scanner is connected. Ready to scan...")
            capture_barcode_data()
        else:
            print("Helett HT20 Barcode Scanner is NOT connected. Waiting for scanner to reconnect...")
            time.sleep(5)  