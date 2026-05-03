# 기본 모듈 
from machine import I2C,Pin
import time

# oled 모듈 
from ssd1306 import SSD1306_I2C

# 한글 모아쓰기 모듈 
from hangul import draw_hangul,H2,V2,X4
import pinno as P
from oled_i2c import addr

# I2C 버스 만들기
SCL_PIN = P.SCL
SDA_PIN = P.SDA
i2c = I2C(0, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))

# oled 인스턴스 만들기
WIDTH  = 64
HEIGHT = 48

oled = SSD1306_I2C(WIDTH, HEIGHT, i2c,addr=addr(i2c)) # addr=0x3c 또는 0x3d
 
def main():  
     
    mode = 0
    mode_str = ['',V2,H2,X4]
    while True:
        # oled를 지움
        oled.fill(0)
        # oled 모듈의 픽셀 쓰기
        oled.text('Abc123',0,0)
        # 한글 모듈의 픽셀 쓰기
        draw_hangul(oled,'한A1',0,10,mode_str[mode])
        # (mode) V2:세로 2배,H2:가로 2배,X4:가로 세로 2배
        # 모드 변경 '' -> V2 -> H2 -> X4
        mode = mode + 1 if mode != 3 else 0
        # oled 표시
        oled.show()
         
        time.sleep_ms(5*1000)
         
if __name__ == '__main__':
    main()