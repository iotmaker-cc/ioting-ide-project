from machine import Pin, I2C, ADC, SPI
from umqtt.simple import MQTTClient
import json
from timerrun import TimerRun
from run import Run
from usemqttclient import UseMQTTClient 
from parse import Parse
import pinno as P
import config as C

# 함수들 이동
run = Run()

temperature = 0
humidity = 0
display_seq = 0 # 교재에는 5로 잘못 표기되어 있음. 
TELEPERIOD = 10

from dht22sensor import DHT22Sensor
dht = DHT22Sensor(pin_gpio=Pin(P.DHT))

from blink import Blink
relay = Blink(pin_instance=Pin(P.RELAY_IN, Pin.OUT), inverted=False)
run.add(relay.run)

from machine import I2C
i2c = I2C(0, scl=Pin(P.SCL), sda=Pin(P.SDA))

from ssd1306 import SSD1306_I2C  # OLED 라이브러리
from hangul import draw_hangul, V2, H2, X4  # 한글 출력 모듈
WIDTH = 64
HEIGHT = 48
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

def display_oled(): 
    global display_seq
    display_seq += 1
    display_seq = display_seq % 2
    if display_seq == 0: 
        oled.fill(0)  # 화면 지우기
        draw_hangul(oled, '온도', 0, 0) 
        draw_hangul(oled, f'{temperature} C', 0, 20)
        oled.show()  # OLED 화면 업데이트
    else: 
        oled.fill(0)  # 화면 지우기
        draw_hangul(oled, '습도', 0, 0) 
        draw_hangul(oled, f'{humidity}', 0, 20)
        oled.show()  # OLED 화면 업데이트    

from timerrun import TimerRun
timer_oled = TimerRun(period=3*1000, callback=display_oled)
run.add(timer_oled.run)

def on_connect_more():
    print('on_connect_more()...')

def callback_more(topic:str,msg:str):
    if topic == f'cmnd/{C.DEVICE}/RELAY':
        relay.set_on_off_str(msg)
        mqtt.publish(f'stat/{C.DEVICE}/RELAY', relay.on_off())

def read_sensors_more():
    global temperature, humidity
    data = dht.read()
    print(data)
    p = Parse(data)
    humidity = p.values[0]
    temperature = p.values[1]
    print(f'{p.keys[1]}: {p.values[1]}, {p.keys[0]}: {p.values[0]} ')
    return data

def mqtt_on_connect():
    print('on_connect() called')
    msg = {'TELEPERIOD': TELEPERIOD}
    mqtt.publish(f'tele/{C.DEVICE}/INFO', msg, retain=True)
    on_connect_more()   

def mqtt_callback(in_topic,in_msg):
    global TELEPERIOD
    topic = in_topic.decode()
    msg   = in_msg.decode()
    print(f'RCV> {topic}, |{msg}|')
    if topic == f'cmnd/{C.DEVICE}/TELEPERIOD':
        TELEPERIOD = int(msg)
        timer_sensor.set(period=TELEPERIOD*1000)
        tele_msg = {'TELEPERIOD': msg}
        mqtt.publish(f'stat/{C.DEVICE}/TELEPERIOD', msg, retain=True)
        mqtt.publish(f'tele/{C.DEVICE}/INFO', tele_msg, retain=True )
        print(f'TELEPERIOD가 {msg}초로 변경되었습니다.')
    else:
        callback_more(topic,msg)

def send_data():
    data = read_sensors_more()
    mqtt.publish(f'tele/{C.DEVICE}/SENSOR',json.dumps(data))

client = MQTTClient(C.MQTT_CLIENT_ID, C.MQTT_SERVER, port=C.MQTT_PORT,
                    user=C.MQTT_USER, password=C.MQTT_PASS, keepalive=60)
mqtt = UseMQTTClient(client, C.DEVICE, C.SSID, C.SSID_PASS, mqtt_callback, mqtt_on_connect)
run.add(mqtt.run)

timer_sensor = TimerRun(period=TELEPERIOD*1000, callback=send_data)
run.add(timer_sensor.run)

def main():        
    while True:
        run.run()

if __name__ == '__main__':
    main()
