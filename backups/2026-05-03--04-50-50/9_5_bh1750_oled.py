from machine import Pin, I2C
from timerrun import TimerRun
from run import Run
from parse import Parse
import pinno as P
import time

brightness = 0

run = Run()

# I2C 설정
i2c = I2C(0, scl=Pin(P.SCL), sda=Pin(P.SDA))

# 조도 센서 설정
from bh1750sensor import BH1750Sensor
bh1750 = BH1750Sensor(i2c)

# OLED 디스플레이 설정
from oled_i2c import addr  # oled i2c addr인 0x3c 또는 0x3d를 돌려줌
from ssd1306 import SSD1306_I2C  # OLED 라이브러리
from hangul import draw_hangul, V2, H2, X4  # 한글 출력 모듈
WIDTH = 64
HEIGHT = 48
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c,addr=addr(i2c)) # addr=0x3c 또는 0x3d

def display_oled(): 
    oled.fill(0)
    draw_hangul(oled, '조도', 0, 0)
    oled.text(f'{brightness} lx', 0, 20)
    oled.show()

def sensor_read():
    global brightness
    data = bh1750.read()  # bh1750 센서에서 데이터를 읽어옴
    print(data)
    p = Parse(data)
    brightness = p.value
    print(f'{p.key}: {p.value}')

    display_oled()

# 타이머 설정
timer_sensor = TimerRun(period=5*1000, callback=sensor_read)
run.add(timer_sensor.run)

def main(): 
    while True:
        run.run()

if __name__ == '__main__':
    main()
