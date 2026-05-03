from machine import Pin, I2C

# 1) I2C 버스 핀 번호 지정하기 
SCL = 36 # ESP32 S3 mini:36, S2 mini:35, C3 mini/Pico:10
SDA = 35 # ESP32 S3 mini:35, S2 mini:33, C3 mini/Pico:8

# 2) I2C 버스 초기화
#    id=0 혹은 id=1 중 하나를 선택. 보드에 따라 다르니 확인하세요.
i2c = I2C(
    0,             # 하드웨어 I2C 버스 번호 (0 또는 1)
    sda=Pin(SDA),  # SDA 핀 번호
    scl=Pin(SCL),  # SCL 핀 번호
    freq=400000    # 통신 속도(Hz)
)

# 3) 연결된 장치 주소 스캔
devices = i2c.scan()


# 4) 예상되는 번지와 이름 나열
i2c_addr = [0x23    , 0x3c  , 0x3d  , 0x68]
i2c_name = ['BH1750', 'OLED', 'OLED', 'RTC']

# 5) 결과 출력
if devices:
    print(f"발견된 I2C 주소:{len(devices)}개")
    for addr in devices:
        try: 
            # 16진수 형태로 보기 편하게 변환
            print(" - ",hex(addr), i2c_name[i2c_addr.index(addr)])
        except ValueError:
            # i2c_name에 없는 번지는 "Unknown"으로 출력 
            print(" - ",hex(addr), "Unknown")
else:
    print("I2C 버스에서 장치를 찾을 수 없습니다.")
