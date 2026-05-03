from machine import Pin, I2C, ADC, SPI
from umqtt.simple import MQTTClient
import json
from timerrun import TimerRun
from run import Run
from usemqttclient import UseMQTTClient
from parse import Parse
import pinno as P
import config as C

run = Run()

gas_value = 0
gas_threshold = 200
brightness = 0
TELEPERIOD = 5 

def on_connect_more():
    print('on_connect_more()...')

def callback_more(topic:str,msg:str):
    global gas_threshold
    
    if topic == f'cmnd/{C.DEVICE}/LED_1':
        led_1.set_on_off_str(msg)
        mqtt.publish(f'stat/{C.DEVICE}/LED_1',led_1.on_off()) 

    elif topic == f'cmnd/{C.DEVICE}/THRESHOLD':
        gas_threshold = int(msg)
        print(f'new {{변수}}: {gas_threshold}')  
        mqtt.publish(f'stat/{C.DEVICE}/THRESHOLD',str(gas_threshold))
    
    display_oled()

def read_sensors_more():

    global brightness,gas_value

    data1 = bh1750.read()
    print(data1)
    p = Parse(data1)
    brightness = p.value
    
    gas_value = gas.read()
    data2 = {"gas": {"value": gas_value}}
    print(f'gas:{gas_value}')   

    if gas_value > gas_threshold:
        bz.begin_blink(on=300,off=200)
    else:
        bz.end_blink()

    display_oled()

    data1.update(data2) # 2 개의 딕셔너리 결합
    
    return data1

def pir_on():
    mqtt.publish(f'tele/{C.DEVICE}/PIR','on',retain=True)
    print('PIR on')

def pir_off():
    mqtt.publish(f'tele/{C.DEVICE}/PIR','off',retain=True)
    print('PIR off')

def display_oled(): 
    oled.fill(0)  # 화면 지우기
    draw_hangul(oled, '가스조도', 0, 0) 
    oled.text(str(gas_value)+'/'+str(gas_threshold), 0, 20) 
    oled.text(str(brightness), 0, 32)
    oled.show()  # OLED 화면 업데이트

from machine import I2C
i2c = I2C(0, scl=Pin(P.SCL), sda=Pin(P.SDA))

from binarysensor import BinarySensor 
pir = BinarySensor(pin_instance=Pin(P.PIR_IN, Pin.IN), inverted=False, callback_on=pir_on, callback_off=pir_off) 
run.add(pir.run)

from bh1750sensor import BH1750Sensor
bh1750 = BH1750Sensor(i2c)

from blink import Blink
led_1 = Blink(pin_instance=Pin(P.LED_1_IN, Pin.OUT), inverted=False)
run.add(led_1.run)

from machine import ADC
gas = ADC(Pin(P.A0_IN))
gas.atten(ADC.ATTN_11DB)

from blink import Blink
bz = Blink(pin_instance=Pin(P.BUZZER_IN, Pin.OUT), inverted=False)
run.add(bz.run)

from ssd1306 import SSD1306_I2C  # OLED 라이브러리
from hangul import draw_hangul, V2, H2, X4  # 한글 출력 모듈
WIDTH = 64
HEIGHT = 48
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

from timerrun import TimerRun
timer_oled = TimerRun(period=3*1000, callback=display_oled)
run.add(timer_oled.run)

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

client = MQTTClient(C.MQTT_CLIENT_ID, C.MQTT_SERVER,port=C.MQTT_PORT,user=C.MQTT_USER, password=C.MQTT_PASS,keepalive=60)
mqtt = UseMQTTClient(client,C.DEVICE,C.SSID,C.SSID_PASS,mqtt_callback,mqtt_on_connect)
run.add(mqtt.run)

timer_sensor = TimerRun(period=TELEPERIOD*1000,callback=send_data)
run.add(timer_sensor.run)

def main():        
    
    while True:
        run.run()
        
if __name__ == '__main__':
    main()
