"""
IOTMAKER ESP32 Kit Demo 프로그램
- ESP32 보드에 연결된 버튼, LED, 릴레이, 버저, 다양한 센서(포텐시오미터, PIR, DS18B20, DHT22, BH1750, DS1307 RTC)와
  SSD1306 OLED 디스플레이를 제어하며 단계별로 동작을 시연합니다.
- 버튼1/2 싱글·더블 클릭으로 스테이지 이동 및 액션 수행
- OLED에 텍스트 및 한글 표시, 시리얼 출력, Buzzer, Relay, LED 제어, 센서 값 읽기/표시
"""

from machine import I2C, Pin, ADC    # I2C, GPIO, ADC 제어를 위한 모듈
import time                            # 타이밍 함수 사용

import pinno as P                     # 핀 번호 정의
# import s3minipinno as P
# import s2minipinno as P

# OLED 디스플레이용 SSD1306 I2C 드라이버
from ssd1306 import SSD1306_I2C

# 한글 모아쓰기 라이브러리
from hangul import draw_hangul, H2, V2, X4

# 버튼 이벤트 처리, 센서 드라이버, RTC, 데이터 파싱 모듈
from button import Button
from ds18b20sensor import DS18B20Sensor
from dht22sensor import DHT22Sensor
from bh1750sensor import BH1750Sensor
from ds1307 import DS1307
from parse import Parse
from oled_i2c import addr  # oled i2c addr인 0x3c 또는 0x3d를 돌려줌


# ───────────────────────────────────────────────────────────────────────────────
# 시간 경과 검사 함수
# duration(ms) 이내라면 True 반환, 초과 시 기준 시각 갱신 후 False 반환
# ───────────────────────────────────────────────────────────────────────────────
def not_elapsed_ms(duration_ms=2000):
    this_ms = time.ticks_ms()
    elapsed_ms = time.ticks_diff(this_ms, v.last_ms)
    if elapsed_ms < duration_ms:
        return True
    else:
        v.last_ms = this_ms
        return False
    
# ───────────────────────────────────────────────────────────────────────────────
# 자동 모드일 때 3초 간격으로 다음 모드로 진행
# ───────────────────────────────────────────────────────────────────────────────
def do_next_func(interval_ms=3000):
    this_ms = time.ticks_ms()
    elapsed_ms = time.ticks_diff(this_ms, v.last_auto_ms)
    if elapsed_ms < interval_ms :
        return 
  
    if v.stage >= len(stage_func) -1:
        return
    else:
        v.last_auto_ms = this_ms
        v.stage += 1
        stage_func[v.stage](seq=Var.INIT)    


# ───────────────────────────────────────────────────────────────────────────────
# 현재 스테이지 인덱스와 전체 스테이지 수를 "현재/전체" 형식의 문자열로 반환
# ───────────────────────────────────────────────────────────────────────────────
def stage_str():
    return f"{v.stage}/{len(stage_func)-1}"

# ───────────────────────────────────────────────────────────────────────────────
# 짧은 기간 부저 울림
# ───────────────────────────────────────────────────────────────────────────────
def short_beep_ms(duration_ms=200):
    bz.value(1); time.sleep_ms(duration_ms); bz.value(0)
    

# ───────────────────────────────────────────────────────────────────────────────
# LED,Relay ON
# ───────────────────────────────────────────────────────────────────────────────
def on_led_relay():
    led1.value(1)
    led2.value(0)
    relay.value(1)
    

# ───────────────────────────────────────────────────────────────────────────────
# LED,Relay OFF
# ───────────────────────────────────────────────────────────────────────────────
def off_led_relay():
    led1.value(0)
    led2.value(1)
    relay.value(0)    


# ───────────────────────────────────────────────────────────────────────────────
# OLED 화면에 v.msg에 담긴 메시지 출력
# - v.oled_type에 따라 한글 모드(HG) 또는 영문 모드(EN) 선택
# - show() 호출로 화면 갱신
# ───────────────────────────────────────────────────────────────────────────────
def show_oled():
    if v.i2c[Var.OLED] == None: return
    oled.fill(0)
    oled.text('st:' + stage_str(), 0, 0)

    if v.oled_type == Var.HG:
        # 한글 모아쓰기 사용
        draw_hangul(oled, v.msg[0], 0, 10)
        oled.text(str(v.msg[1]), 0, 28)
        oled.text(str(v.msg[2]), 0, 38)
    else:
        # 일반 텍스트 출력
        oled.text(str(v.msg[0]), 0, 10)
        oled.text(str(v.msg[1]), 0, 20)
        oled.text(str(v.msg[2]), 0, 30)
        oled.text(str(v.msg[3]), 0, 40)

    oled.show()


# ───────────────────────────────────────────────────────────────────────────────
# 센서 값(v.msg[1], v.msg[2])이 변경되었으면 OLED와 콘솔에 출력
# ───────────────────────────────────────────────────────────────────────────────
def show_new_sensor_value():
    if v.last_msg[1] != v.msg[1] or v.last_msg[2] != v.msg[2]:
        show_oled()
        print(' -', v.msg[1], v.msg[2], v.msg[3])
        v.last_msg[1] = v.msg[1]
        v.last_msg[2] = v.msg[2]


# ───────────────────────────────────────────────────────────────────────────────
# 버튼1 싱글 클릭: 다음 스테이지로 이동 후 INIT 시퀀스 실행
# ───────────────────────────────────────────────────────────────────────────────
def button1_single_resp(response):
    v.stage = min(v.stage + 1, len(stage_func) - 1)
    stage_func[v.stage](seq=Var.INIT)


# ───────────────────────────────────────────────────────────────────────────────
# 버튼1 더블 클릭: 현재 스테이지가 led_relay_on이면 액션 수행 후 INIT
# ───────────────────────────────────────────────────────────────────────────────
def button1_double_resp(response):
    if stage_func[v.stage] == double_click_btn1:
        v.stage += 1
        stage_func[v.stage](seq=Var.INIT)
    
# ───────────────────────────────────────────────────────────────────────────────
# 버튼1 트리플 클릭: 현재 스테이지가 v.auto를 토글함
# ───────────────────────────────────────────────────────────────────────────────

def button1_triple_resp(response):
    v.auto = not v.auto
    print(f'자동 모드가 {v.auto}로 바뀜')
    print('첫 스테이지로 이동')
    v.stage = 0
    v.last_auto_ms = time.ticks_ms()
    stage_func[v.stage](seq=Var.INIT)
    
    
# ───────────────────────────────────────────────────────────────────────────────
# 버튼2 싱글 클릭: 이전 스테이지로 이동 후 INIT 시퀀스 실행
# ───────────────────────────────────────────────────────────────────────────────
def button2_single_resp(response):
    v.stage = max(v.stage - 1, 0)
    stage_func[v.stage](seq=Var.INIT)


# ───────────────────────────────────────────────────────────────────────────────
# 버튼2 더블 클릭: 현재 스테이지가 led_relay_off이면 액션 수행 후 INIT
# ───────────────────────────────────────────────────────────────────────────────
def button2_double_resp(response):
    if stage_func[v.stage] == double_click_btn2:
        v.stage += 1
        stage_func[v.stage](seq=Var.INIT)
        
# ───────────────────────────────────────────────────────────────────────────────
# 버튼2 트리플 클릭: 첫 스테이지로 이동
# ───────────────────────────────────────────────────────────────────────────────
def button2_triple_resp(response):
    print('첫 스테이지로 이동')
    v.stage = 0
    v.last_auto_ms = time.ticks_ms()
    stage_func[v.stage](seq=Var.INIT)

# ───────────────────────────────────────────────────────────────────────────────
# 각 스테이지별 INIT/ SENSOR 동작 정의
# - INIT: OLED 메시지 초기화, 버튼 안내, 센서 인스턴스 생성 등
# - SENSOR: 주기별 센서 읽기 및 화면/콘솔 업데이트
# ───────────────────────────────────────────────────────────────────────────────

def double_click_btn1(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '더블클릭'
        v.msg[1] = 'BTN1'
        show_oled()
    
        print(stage_str() + " 버튼1을 더블클릭하세요")
        
        short_beep_ms()
        
def double_click_btn2(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '더블클릭'
        v.msg[1] = 'BTN2'
        show_oled()
        
        print(stage_str() + " 버튼2을 더블클릭하세요")
        
        short_beep_ms()
        
def next_prev(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'Button'
        v.msg[1] = '1:Next'
        v.msg[2] = '2:Prev'
        v.oled_type = Var.EN
        show_oled()
        
        print(stage_str() + " 버튼1:다음, 버튼2:이전")
        
        short_beep_ms()
        
def triple_auto(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'Button1'
        v.msg[1] = 'triple'
        v.msg[2] = '>>auto'
        v.msg[3] = 'toggle'
        v.oled_type = Var.EN
        show_oled()
        
        print(stage_str() + " 버튼1을 3번 클릭 >> 자동/수동 토글")
        
        short_beep_ms()


def display_auto(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'AutoMode'
        v.msg[1] = f'{v.auto}'
        v.oled_type = Var.EN
        show_oled()
        
        print(stage_str() + f" 자동 모드는 {v.auto}입니다.")
        
        short_beep_ms()
    
def led_relay_on(seq):
    if seq == Var.INIT:
        on_led_relay()        
        v.init_oled_msg();
        v.msg[0] = 'ONstatus';
        v.msg[1] = 'Led1 ON'
        v.msg[2] = 'Led2 ON'
        v.msg[3] = 'RelayON'        
        v.oled_type = Var.EN        
        show_oled()
        print(stage_str() + " ON 상태(Led1,Led2,Relay)")
        
        short_beep_ms()


def led_relay_off(seq):
    if seq == Var.INIT:
        off_led_relay()    
        
        v.init_oled_msg();
        v.msg[0] = 'OFFstatus';
        v.msg[1] = 'Led1 OFF'
        v.msg[2] = 'Led2 OFF'
        v.msg[3] = 'RelayOFF'        
        v.oled_type = Var.EN        
        show_oled()
        
        print(stage_str() + " OFF 상태(Led1,Led2,Relay)")
        
        short_beep_ms()

    
def display_i2c(seq):
    
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'I2C:'
        v.oled_type = Var.EN
        
        print(stage_str() + " I2C 번지")
        
        devices = i2c.scan()
        if not devices:
            print(" -", "I2C 장치가 연결되지 않았습니다.")
            return
    
        name_by_addr = {0x23:'BH1750', 0x3c:'OLED', 0x3d:'OLED', 0x68:'RTC'}
        indx_by_addr  = {0x23:Var.BH1750, 0x3c:Var.OLED, 0x3d:Var.OLED, 0x68:Var.RTC}

        for i, addr in enumerate(devices):
            if i >= 3:
                break

            i2c_name = name_by_addr.get(addr, 'None')
            indx = indx_by_addr.get(addr)

            if indx is not None:
                v.i2c[indx] = addr

            v.msg[i+1] = f'{addr:02x} {i2c_name}'
            print(f' - 0x{addr:02x} {i2c_name}')
            
        show_oled()
        
        short_beep_ms()
        

def read_potentiometer(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '포텐:'
        show_oled()
        
        print(stage_str() + " 포텐시오미터 읽기")
        
        short_beep_ms()
        v.last_ms = time.ticks_ms() - 5000
        
    elif seq == Var.SENSOR:
        if not_elapsed_ms(1000): return
        val = potentiometer.read()
        v.msg[1] = f"{int((val/4095)*100)}%"
        show_new_sensor_value()


def read_pir(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '동작:'
        show_oled()
        print(stage_str() + " PIR 모션 감지")
        
        short_beep_ms()
        
    elif seq == Var.SENSOR:
        v.msg[1] = ['off','on'][pir.value()]
        show_new_sensor_value()


def read_ds18b20(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'DS18B20:'
        v.oled_type = Var.EN
        show_oled()
        print(stage_str() + " DS18B20 온도 센서")
        v.instance = DS18B20Sensor(pin_gpio=P.DS18B20_IN)
        
        short_beep_ms()
        v.last_ms = time.ticks_ms() - 5000
        
    elif seq == Var.SENSOR:
        if not_elapsed_ms(5000): return
        data = v.instance.read()
        p = Parse(data)
        v.msg[1] = f"{p.ow_values[0]}'C"
        v.msg[2] = p.ow_ids[0][:8]
        v.msg[3] = p.ow_ids[0][8:]
        show_new_sensor_value()


def read_dht22(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'DHT22:'
        v.oled_type = Var.EN
        show_oled()
        print(stage_str() + " DHT22 온습도 센서")
        v.instance = DHT22Sensor(P.DHT, ser="001")
        
        short_beep_ms()
        v.last_ms = time.ticks_ms() - 5000
        
    elif seq == Var.SENSOR:
        if not_elapsed_ms(5000): return
        data = v.instance.read()
        p = Parse(data)
        v.msg[1] = f"{p.values[1]}'C"; v.msg[2] = f"{p.values[0]}%"
        show_new_sensor_value()


def read_bh1750(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '조도:'
        print(stage_str() + " BH1750 조도 센서")
        
        if v.i2c[Var.BH1750] != None:
            v.instance = BH1750Sensor(i2c_bus=i2c)
            
        show_oled()            
        
        short_beep_ms()
        v.last_ms = time.ticks_ms() - 5000
        
    elif seq == Var.SENSOR:
        if not_elapsed_ms(5000): return
        if v.i2c[Var.BH1750] == None:
            v.msg[1] = "No device"
        else:
            data = v.instance.read()
            p = Parse(data)
            v.msg[1] = f"{p.value} lx"
        show_new_sensor_value()


def read_time(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = 'DateTime'
        v.oled_type = Var.EN
        print(stage_str() + " RTC Date/Time")        
        if v.i2c[Var.RTC] != None:
            v.instance = DS1307(i2c=i2c)
        show_oled()
        
        short_beep_ms()
        v.last_ms = time.ticks_ms() - 5000
        
    elif seq == Var.SENSOR:
        if not_elapsed_ms(100): return
        if v.i2c[Var.RTC] == None:
            v.msg[1] = "No device"
        else:
            y,m,d,h,mi,s,wd,ss = v.instance.datetime
            v.msg[1] = f"{y:02d}-{m:02d}-{d:02d}"[2:]
            v.msg[2] = f"{h:02d}:{mi:02d}:{s:02d}"
        show_new_sensor_value()
        

def last_stage(seq):
    if seq == Var.INIT:
        off_led_relay()
        v.init_oled_msg()
        v.msg[0] = '마지막:'
        show_oled()
        print(stage_str() + " 종료 단계")
        print('End of IOTMAKER ESP32 Kit Demo')
        
        short_beep_ms()


# 스테이지 함수 리스트: 인덱스별로 위 함수 매핑
stage_func = [
    double_click_btn1, double_click_btn2, next_prev, display_i2c, 
    read_time, led_relay_on, led_relay_off, 
    read_potentiometer, read_pir, read_ds18b20, read_dht22,
    read_bh1750, last_stage
]


# ───────────────────────────────────────────────────────────────────────────────
# 전역 상태 관리용 클래스 Var
# - __slots__로 속성 고정, 미정의 속성 설정 시 에러 발생
# - stage, 메시지, 센서 인스턴스, I2C 정보 등 보관
# ───────────────────────────────────────────────────────────────────────────────
class Var:
    INIT = 1
    SENSOR = 2
    EN = 1
    HG = 2
    
    OLED   = 0
    RTC    = 1
    BH1750 = 2
    NO_OF_I2C = 3
    

    __slots__ = (
        'stage', 'msg', 'last_msg', 'oled_type','i2c',
        'instance', 'last_ms', 'auto','last_auto_ms'
    )

    def __setattr__(self, name, value):
        if name not in self.__slots__:
            raise AttributeError(f"Var has no attribute '{name}'")
        super().__setattr__(name, value)

    def __init__(self):
        # 초기값 설정
        self.stage     = 0
        self.msg       = [''] * 4
        self.last_msg  = [''] * 4
        self.oled_type = Var.HG
        self.i2c       = [None] * Var.NO_OF_I2C
        self.instance  = None
        self.last_ms   = 0
        self.auto      = False
        self.last_auto_ms = 0

    def init_oled_msg(self):
        # OLED 메시지 버퍼 초기화
        for i in range(len(self.msg)):
            self.msg[i] = ''
            self.last_msg[i] = ''
        self.oled_type = Var.HG


# ───────────────────────────────────────────────────────────────────────────────
# 전역 객체 및 하드웨어 초기화
# ───────────────────────────────────────────────────────────────────────────────
v = Var()

# LED & Relay 설정
led1 = Pin(P.LED_1_IN, Pin.OUT); led1.value(0)
led2 = Pin(P.LED_2_IN, Pin.OUT); led2.value(1)  # inverted wiring
relay = Pin(P.RELAY_IN, Pin.OUT); relay.value(0)

# 버튼 설정 (싱글/더블 클릭 이벤트 연결)
btn1 = Button(Pin(P.BUTTON_1_IN, Pin.IN, Pin.PULL_UP), inverted=True)
btn2 = Button(Pin(P.BUTTON_2_IN, Pin.IN, Pin.PULL_DOWN), inverted=False)
btn1.add(Button.SINGLE, callback=button1_single_resp)
btn1.add(Button.DOUBLE, callback=button1_double_resp)
btn1.add(Button.TRIPLE, callback=button1_triple_resp)
btn2.add(Button.SINGLE, callback=button2_single_resp)
btn2.add(Button.DOUBLE, callback=button2_double_resp)
btn2.add(Button.TRIPLE, callback=button2_triple_resp)

# 부저, PIR 모션 센서
bz = Pin(P.BUZZER_IN, Pin.OUT)
pir = Pin(P.PIR_IN, Pin.IN)

# ADC: 포텐시오미터
potentiometer = ADC(Pin(P.L2_IN))
potentiometer.atten(ADC.ATTN_11DB)  # 최대 3.3V 측정

print('Start of IOTMAKER ESP32 Kit Demo')

# I2C, OLED 초기화
i2c = I2C(0, scl=Pin(P.SCL), sda=Pin(P.SDA))
v.i2c[Var.OLED] = addr(i2c)
if v.i2c[Var.OLED] == None:
    print("The messages wiil be printed only.")
else:
    oled = SSD1306_I2C(64, 48, i2c,addr=v.i2c[Var.OLED]) # addr=0x3c 또는 0x3d

# 시작 스테이지 표시
v.stage = 0
stage_func[v.stage](seq=Var.INIT)

# ───────────────────────────────────────────────────────────────────────────────
# 메인 루프: 버튼 이벤트 처리 및 현재 스테이지 SENSOR 시퀀스 반복 실행
# ───────────────────────────────────────────────────────────────────────────────
def main():
    try:
        while True:
            btn1.run()
            btn2.run()
            stage_func[v.stage](seq=Var.SENSOR)
            
            if v.auto == True:
                do_next_func()
    except KeyboardInterrupt:
        print("KeyboardInterrupt 감지! 프로그램 종료")


if __name__ == '__main__':
    main()









































































































































