# file: usemqttclient
import network
import time
import machine
import binascii
from umqtt.simple import MQTTClient
import ujson as json

class CommControl:
    """
    MQTT 클라이언트를 사용하여 Wi-Fi 및 MQTT 연결을 관리하는 클래스입니다.

    :param client: MQTT 클라이언트 객체
    :param device: 장치 이름
    :param ssid: Wi-Fi SSID
    :param ssid_pass: Wi-Fi 비밀번호
    :param callback: MQTT 메시지 수신 시 호출될 콜백 함수
    :param on_connect: MQTT 연결이 성공했을 때 호출될 함수 (선택 사항)
    """
    
    CHECK_COMM = False
    
    def __init__(self, client, device, ssid, ssid_pass, callback, on_connect=None):
        self.device = device
        self.ssid = ssid
        self.ssid_pass = ssid_pass
        self.client = client
        self.on_connect = on_connect
        self.callback = callback
        
        self.wifi_try_count = 10
        self._connect_wifi()
        
        self.prev_wifi_connected = False
        self.mqtt_connected = False
        self.prev_mqtt_connected = False
        
        self.mqtt_try = False
        self.mqtt_try_interval = 30 * 1000
        self.mqtt_try_ms = 0
        
        self.check_comm = CommControl.CHECK_COMM      
        self.check_comm_ms = 0
        self.check_comm_interval = 10 * 1000
        
        self.temp = None

    def subscribe(self, topic, qos=0):
        """
        특정 토픽에 대한 구독을 설정합니다.

        :param topic: 구독할 토픽
        :param qos: QoS (Quality of Service) 레벨, 기본값은 0
        :return: 구독 성공 여부와 에러 메시지 (성공 시 빈 문자열)
        """
        try:        
            self.client.subscribe(topic, qos)
            print(f'sub> {topic}, qos={qos}')
            return True, ''
        except Exception as e:
            print(f'sub> error {e}, {topic}')
            return False, e

    def publish(self, topic, msg, retain=False, qos=0):
        """
        특정 토픽으로 메시지를 발행합니다.

        :param topic: 발행할 토픽
        :param msg: 발행할 메시지 (딕셔너리, 정수, 실수, 불리언일 경우 자동 변환됨)
        :param retain: 메시지를 유지할지 여부, 기본값은 False
        :param qos: QoS (Quality of Service) 레벨, 기본값은 0
        :return: 발행 성공 여부와 에러 메시지 (성공 시 빈 문자열)
        """
 
        if isinstance(msg, dict):
            msg = json.dumps(msg)
        elif isinstance(msg, (int, float, bool)):
            msg = str(msg)
        
        try:
            self.client.publish(topic, msg, retain, qos)
            print(f'pub> {topic}, |{msg}|, retain={retain}, qos={qos}')
            return True, ''
        except Exception as e:
            print(f'pub> error {e}, {topic}, |{msg}|')
            return False, e

    def _connect_wifi(self):
        """
        Wi-Fi 연결을 시도합니다.

        :return: Wi-Fi 연결 성공 여부
        """
        try:
            self.wlan = network.WLAN(network.STA_IF)
            self.wlan.active(True)
            print(f'connect_wifi> Wi-Fi 시작({self.ssid})...')
            
            self.wlan.connect(self.ssid, self.ssid_pass)
            
            connected = False
            for _ in range(self.wifi_try_count):
                if self.wlan.isconnected:
                    connected = True
                    break
                print('connect_wifi> Wi-Fi 연결 중...')
                time.sleep(1)
            
            if connected:
                print('connect_wifi> Wi-Fi 연결 완료:', self.wlan.ifconfig())
                return True
            else:
                print("connect_wifi> Wi-Fi 연결 실패. 시간 경과...")
                return False
        except OSError as e:
            print(f'connect_wifi> OSError: 와이파이 연결 안됨 {e}')
            return False

    def set(self, check_comm=None, mqtt_try_interval_sec=None, check_comm_interval_sec=None):
        """
        통신 설정을 변경합니다.

        :param check_comm: 통신 점검 기능 사용 여부
        :param mqtt_try_interval_sec: MQTT 재연결 시도 간격 (초 단위)
        :param check_comm_interval_sec: 통신 점검 간격 (초 단위)
        """
        if check_comm is not None:
            self.check_comm = check_comm
        if mqtt_try_interval_sec is not None:
            self.mqtt_try_interval = mqtt_try_interval_sec * 1000
        if check_comm_interval_sec is not None:
            self.check_comm_interval = check_comm_interval_sec * 1000        

    def _connect_mqtt(self) -> bool:
        """
        MQTT 연결을 시도합니다.

        :return: MQTT 연결 성공 여부
        """
        if not self.wlan.isconnected():
            print('connect_mqtt> WiFi not connected')
            return False
        try:
            print('connect_mqtt> MQTT 연결 시작')
            self.set_last_will_template()
            self.client.connect()
            print('connect_mqtt> MQTT 연결 완료')        
            self.on_connect_template()
            self.mqtt_connected = True
            self.mqtt_try = False
            return True
        except Exception as e:
            print(f'connect_mqtt> MQTT 연결 실패: {e}')
            return False

    def set_last_will_template(self):
        """
        MQTT 유언 메시지를 설정합니다.
        """
        self.client.set_last_will(f'tele/{self.device}/LWT', 'Offline', retain=True)
        print(f'LWT> tele/{self.device}/LWT, |Offline|, retain=True')

    def on_connect_template(self):
        """
        MQTT 연결 성공 시 실행할 초기화 작업을 수행합니다.
        """
        self.client.set_callback(self.callback)
        self.publish(f'tele/{self.device}/LWT', 'Online', retain=True)
        self.subscribe(f'cmnd/{self.device}/#')
        if self.on_connect:
            self.on_connect()
            
    def connect(self):
        pass

    def run(self):
        """
        주기적으로 실행되어 Wi-Fi 및 MQTT 연결 상태를 점검하고,
        필요한 경우 재연결을 시도합니다.
        """
        try:
            if self.mqtt_connected:
                self.client.check_msg()
        except OSError as e:
            print(f'ckeck_msg> {e}')
            self.mqtt_connected = False
            self.mqtt_try = True
            self.mqtt_try_ms = time.ticks_ms()
        
        if self.check_comm and time.ticks_diff(time.ticks_ms(), self.check_comm_ms) > self.check_comm_interval:
            self.check_comm_ms = time.ticks_ms()
            if self.wlan.isconnected:
                try:
                    self.client.ping()
                    self.mqtt_connected = True
                except Exception:
                    self.mqtt_connected = False
            print(f'check_comm> WiFi: {self.wlan.isconnected()}, MQTT: {self.mqtt_connected}')
        
        if self.wlan.isconnected() and not self.prev_wifi_connected:
            self.prev_wifi_connected = self.wlan.isconnected()
            self.mqtt_try = True
            self.mqtt_try_ms = time.ticks_ms()
            self._connect_mqtt()
        
        if self.mqtt_try and time.ticks_diff(time.ticks_ms(), self.mqtt_try_ms) > self.mqtt_try_interval:
            self.mqtt_try_ms = time.ticks_ms()
            self._connect_mqtt()

def main():
    import network
    import time
    import machine
    import binascii
    from umqtt.simple import MQTTClient
    import ujson as json
            
    # config
    import config as C
    """
    # config.py의 내용 본인 것으로 수정하여 디바이스에 설치하여야 합니다.
    DEVICE = 'ESP32-01'

    SSID = 'my-ssid'                # 실제 값으로 변경
    SSID_PASS = 'my-ssid-pass'      # 실제 값으로 변경
    
    MQTT_SERVER = '192.168.xxx.xxx' # 실제 값으로 변경
    MQTT_PORT = 1883
    MQTT_USER = 'SECOND_USER'
    MQTT_PASS = 'SECOND_PASSWORD'

    import binascii
    import machine

    MQTT_CLIENT_ID = binascii.hexlify(machine.unique_id()).decode()
    """

    DEVICE    = C.DEVICE
    SSID      = C.SSID
    SSID_PASS = C.SSID_PASS

    MQTT_SERVER = C.MQTT_SERVER
    MQTT_PORT = C.MQTT_PORT
    MQTT_USER = C.MQTT_USER
    MQTT_PASS = C.MQTT_PASS
    MQTT_CLIENT_ID = binascii.hexlify(machine.unique_id()).decode()
    
    def on_connect():
        print('on_connect() called')
        msg = {'TELEPERIOD': 10}
        mqtt.publish(f'tele/{C.DEVICE}/INFO', msg, retain=True)   

    def callback(in_topic,in_msg):
        topic = in_topic.decode()
        msg   = in_msg.decode()
        
        print(f'RCV> {topic}, |{msg}|')
        
        try:        
            if topic == f'cmnd/{C.DEVICE}/TELEPERIOD':
                sensor_timer.set(period=int(msg)*1000)
                tele_msg = {'TELEPERIOD': msg}
                mqtt.publish(f'stat/{C.DEVICE}/TELEPERIOD', msg, retain=True)
                mqtt.publish(f'tele/{C.DEVICE}/INFO', tele_msg, retain=True )
                print(f'TELEPERIOD가 {msg}초로 변경되었습니다.')
        except ValueError:
            print('msg가 숫자가 아님.')            
    
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_SERVER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASS, keepalive=60)
    mqtt = CommControl(client,DEVICE,SSID,SSID_PASS,callback,on_connect)
    
    mqtt.temp = {
        'ser': 0
    }
    
    def send_sensor():
        mqtt.temp['ser'] += 1
        mqtt.publish(f'tele/{DEVICE}/SENSOR',json.dumps(mqtt.temp))
        #client.publish(f'tele/{DEVICE}/SENSOR',json.dumps(data))
        
    from timerrun import TimerRun
    sensor_timer = TimerRun(period=10*1000)
    sensor_timer.add(send_sensor)
    while True:
        mqtt.run()
        sensor_timer.run()
        
if __name__ == '__main__':
    main()        
        

