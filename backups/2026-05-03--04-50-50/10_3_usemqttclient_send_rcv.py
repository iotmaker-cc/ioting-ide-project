from umqtt.simple import MQTTClient
import ujson as json

from timerrun import TimerRun
from usemqttclient import UseMQTTClient 
import config as C

def on_connect():
    print('on_connect() called')
    msg = {'TELEPERIOD': 10}
    mqtt.publish(f'tele/{C.DEVICE}/INFO', msg, retain=True)   

def callback(in_topic,in_msg):
    topic = in_topic.decode()
    msg   = in_msg.decode()
    
    print(f'RCV> {topic}, |{msg}|')
           
    if topic == f'cmnd/{C.DEVICE}/TELEPERIOD':
        sensor_timer.set(period=int(msg)*1000)
        tele_msg = {'TELEPERIOD': msg}
        mqtt.publish(f'stat/{C.DEVICE}/TELEPERIOD', msg, retain=True)
        mqtt.publish(f'tele/{C.DEVICE}/INFO', tele_msg, retain=True )
        print(f'TELEPERIOD가 {msg}초로 변경되었습니다.')

ser = 0
def send_sensor():
    global ser
    ser += 1
    data = {
        'ser': ser
    }
    mqtt.publish(f'tele/{C.DEVICE}/SENSOR',json.dumps(data))
    
client = MQTTClient(C.MQTT_CLIENT_ID, C.MQTT_SERVER,port=C.MQTT_PORT,user=C.MQTT_USER, password=C.MQTT_PASS,keepalive=60)
mqtt = UseMQTTClient(client,C.DEVICE,C.SSID,C.SSID_PASS,callback,on_connect)

from timerrun import TimerRun
sensor_timer = TimerRun(period=10*1000)
sensor_timer.add(send_sensor)

def main():        
    
    while True:
        mqtt.run()
        sensor_timer.run()
        
if __name__ == '__main__':
    main()        
        