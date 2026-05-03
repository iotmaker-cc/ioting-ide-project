# config.py
DEVICE = 'ESP32-01'
 
SSID      = 'your_ssid'         # 본인의 것
SSID_PASS = 'your_password'     # 본인의 것
MQTT_SERVER = '192.168.225.175' # 실제 값으로 변경
 
MQTT_PORT = 1883
MQTT_USER = 'user'
MQTT_PASS = 'passwd'
 
import binascii
import machine
 
MQTT_CLIENT_ID = binascii.hexlify(machine.unique_id()).decode()
