# s3minipinno.py --> 개발보드 \lib\pinno.py

# 내장 핀 
BUILTIN_RGB = 47
BUILTIN_BTN = 0

# 외부핀 사용
R1 = TX = 43
R2 = RX = 44
R3 = D1 = SCL = RELAY = 36
R4 = D2 = SDA = DS18B20 = WS2812B = 35
R5 = D3 = PIR = BTN = 18
R6 = D4 = DHT = DHT11 = DHT22 = 16

L2 = A0 = POTENTIOMETER = 2
L3 = D0 = BUTTON_1 = 4
L4 = D5 = SCK  = BUTTON_2 = 12
L5 = D6 = MISO = LED_1 = 13
L6 = D7 = MOSI = LED_2 = 11
L7 = D8 = CS   = BUZZER = 10

# 내부핀 사용
R1_IN = TX_IN = 33
R2_IN = RX_IN = 37
R3_IN = D1_IN = SDA_IN = RELAY_IN = 38
R4_IN = D2_IN = SCL_IN = DS18B20_IN = WS2812B_IN = 34
R5_IN = D3_IN = PIR_IN = BTN_IN = 21
R6_IN = D4_IN = DHT_IN = DHT11_IN = DHT22_IN = 17

L1_IN         = 1
L2_IN = A0_IN = POTENTIOMETER_IN = 3
L3_IN = D0_IN = BUTTON_1_IN = 5
L4_IN = D5_IN = BUTTON_2_IN = 6
L5_IN = D6_IN = LED_1_IN = 7
L6_IN = D7_IN = LED_2_IN = 8
L7_IN = D8_IN = BUZZER_IN = 9

from machine import Pin
import time

# 1. 부저 핀 객체 생성 (출력 모드)
buzzer = Pin(BUZZER_IN, Pin.OUT)

def buzz(on_time_ms: int, off_time_ms: int = 0):
    """
    부저를 켜고(on_time_ms) 끕니다(off_time_ms).
    off_time_ms를 생략하면 켜기만 합니다.
    """
    buzzer.value(1)               # 부저 on
    time.sleep_ms(on_time_ms)     # 지정된 시간(ms) 대기
    buzzer.value(0)               # 부저 off
    if off_time_ms > 0:
        time.sleep_ms(off_time_ms)

# 2. 메인 루프: 500ms 울리고 500ms 쉬기 반복
if __name__ == "__main__":
    while True:
        buzz(500, 500)
