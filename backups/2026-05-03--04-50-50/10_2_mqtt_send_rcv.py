import network
from umqtt.simple import MQTTClient
import json
import binascii
import time
import machine  # 교재에는 누락되어 있습니다.
# 디바이스 설정    
DEVICE    = 'ESP32-01'

# WiFi 설정
SSID      = 'your_ssid'         # 본인의 것
SSID_PASS = 'your_password'     # 본인의 것

MQTT_SERVER = '192.168.225.175'  # 본인의 것\
MQTT_PORT   = 1883
MQTT_USER   = 'SECOND_USER'     # pw.txt에 등록된 것
MQTT_PASSWORD   = 'SECOND_PASSWORD' # pw.txt에 등록된 것

MQTT_CLIENT_ID = binascii.hexlify(machine.unique_id()).decode()

print('MQTT_CLIENT_ID:',MQTT_CLIENT_ID)
wlan = None 
client = None

# Wi-Fi 연결 함수
def connect_wifi():
    global wlan
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Wi-Fi 연결 중...')
        wlan.connect(SSID, SSID_PASS)
        while not wlan.isconnected():
            time.sleep(1)
    print('Wi-Fi 연결 완료:', wlan.ifconfig())

# MQTT 메시지를 받으면 실행되는 콜백 함수
def sub_callback(in_topic, in_msg):
    topic = in_topic.decode()
    msg = in_msg.decode()
    
    print(f'메시지 수신> topic:{topic}, msg:{msg}')
    if topic == f'cmnd/{DEVICE}/TELEPERIOD':
        sensor_timer.set(period=int(msg)*1000)
        print(f'TELEPERIOD가 {msg}초로 변경되었습니다.')

# MQTT 클라이언트 설정 및 연결
def connect_mqtt():
    global client
    client = MQTTClient(client_id=MQTT_CLIENT_ID, server=MQTT_SERVER,
             port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD) 
    client.set_callback(sub_callback)
    client.connect()
    print('MQTT 서버 연결 완료')
    
    return client

# 메시지 발행 함수
ser = 0
def send_sensor():
    global ser
    ser += 1
    data = {
        'ser': ser
    }
    temperature = 25  # 임의의 온도 데이터
    client.publish(f'tele/{DEVICE}/SENSOR', json.dumps(data))
    print(f'데이터 발행됨',data)

# 메인 프로그램

from timerrun import TimerRun
sensor_timer = TimerRun(period=10*1000)
sensor_timer.add(send_sensor)

# 1. Wi-Fi 연결
connect_wifi()

# 2. MQTT 연결
client = connect_mqtt()

# 3. 토픽 구독
client.subscribe(f'cmnd/{DEVICE}/#')
print(f"cmnd/{DEVICE}/# 토픽 구독 중...")    

def main():    

    # 4. 주기적으로 메시지 발행 및 메시지 수신 대기
    while True:
        sensor_timer.run()
        client.check_msg()  # 비동기적으로 메시지 수신 확인

# 프로그램 시작
if __name__ == "__main__":
    main()
