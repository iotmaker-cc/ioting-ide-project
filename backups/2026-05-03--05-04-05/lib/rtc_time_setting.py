import ds1307
from machine import I2C, Pin
import pinno
import time

# I2C 핀 설정 (ESP32)
i2c = I2C(0, scl=Pin(pinno.SCL), sda=Pin(pinno.SDA))

# DS1307 RTC 객체 생성
rtc = ds1307.DS1307(i2c)

def datetime_str(dt: tuple) -> str:
    #(y,m,d,H,M,S,w,SS)  = rtc.datetime
    return f'{dt[0]}-{dt[1]:02}-{dt[2]:02}T{dt[3]:02}:{dt[4]:02}:{dt[5]:02}'

def w_str(dt: tuple) -> str:
    wstr = ['월','화','수','목','금','토','일']
    return wstr[dt[6]]

# 현재 시간을 설정 (연, 월, 일, 요일, 시, 분, 초)
#rtc.datetime((2024, 10, 3, 2, 14, 30, 0))  # 2024년 10월 3일 목요일 14시 30분 0초
rtc.datetime = (2024, 12, 30, 03, 08, 00, 0)  # 0:월,1:화,2:수,3:목,4:금,5:토,6:일
# 현재 시간 읽기
while True:
    current_time = rtc.datetime
    (y,m,d,H,M,S,w,SS)  = rtc.datetime    
    #print(f'{y}-{m:01}-{d:02}T{H:02}-{M:02}-{S:02}',current_time)
    print(datetime_str(rtc.datetime),w_str(rtc.datetime))
    time.sleep(1)
