
import time
from ssd1306 import SSD1306_I2C
def addr(i2c):
    """
    I2C 버스에서 OLED 디스플레이의 주소를 스캔하여 반환합니다.

    주어진 I2C 객체를 통해 연결된 장치를 검색하고,
    일반적으로 사용되는 OLED 주소 0x3C 또는 0x3D가 발견되면 해당 주소를 반환합니다.
    발견되지 않을 경우 None을 반환합니다.

    Args:
        i2c (I2C): 초기화된 I2C 버스 객체.

    Returns:
        int: OLED 디스플레이의 I2C 주소 (0x3C 또는 0x3D).
    """
    oled_i2c = None
    oled_i2c_1st = None
    oled_i2c_2nd = None
    
    devices = i2c.scan()
    
    if not devices:
        print("No I2C Devices found.")
        return oled_i2c
    
    for addr in devices:
        if addr == 0x3c or addr == 0x3d:
            oled_i2c_1st = addr
            oled_i2c     = addr
        
    if oled_i2c == None:
        print("No OLED Device found.")
        return oled_i2c    
                
    """
    OLED 실드의 회로가 균일하지 못하여 I2C 번지가 다음의 3가지 경우로 나타납니다.
    - 0x3c인 경우
    - 0x3d인 경우
    - 처음에는 0x3c이다가 이후에는 0x3d인 경우
    
    이 문제를 해결하기 위하여
    - 처음으로 나타나는 I2C번지를 사용하여 임시로 OLED 인스턴스를 만들고
    - 1초 후에 다시 I2C 번지를 찾아서 사용하기로 합니다.
    """
    
    # 임시로 첫 번째 인스턴스를 만듭니다.
    _ = SSD1306_I2C(64, 48, i2c,oled_i2c_1st) # addr=0x3c 또는 0x3d
    time.sleep(1)
    
    # 두 번째 나타나느 I2C 번지를 찾기로 함
    
    devices = i2c.scan()
    
    if not devices:
        print("No I2C Devices found.")
        return oled_i2c
    
    for addr in devices:
        if addr == 0x3c or addr == 0x3d:
            oled_i2c_2nd = addr
            oled_i2c     = addr
        
    if oled_i2c == None:
        print("No OLED Device found.")

    elif oled_i2c_1st == oled_i2c_2nd:
        print(f'oled i2c addr:{hex(oled_i2c_2nd)}')
    else:
        print(f'oled i2c addr 1st:{hex(oled_i2c_1st)}')
        print(f'oled i2c addr 2nd:{hex(oled_i2c_2nd)}')
        
    return oled_i2c
