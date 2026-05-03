"""
BinarySensor Class for MicroPython
version: 1.0(2024.11)
Copyright by: YANG Jaesam (iotmaker.cc@gmail.com)
All code is released under the MIT licence.
The author makes no warranties regarding this software.

file name: binarysensor.py
"""

from machine import Pin
import time

class BinarySensor:
    
    PULL_UP = Pin.PULL_UP
    PULL_DOWN = Pin.PULL_DOWN
    DEBOUNCE_MS = 20

    def __init__(self,pin_instance,*,inverted=False, callback_on=None, callback_off=None):     
                       
        self.pin = pin_instance
        self.inverted = inverted 

        if self.inverted:
            self.ON = 0
        else:
            self.ON = 1
            
        self.OFF = not self.ON

        # 이벤트 타입을 위한 콜백 저장소
        self.callback_on = callback_on
        self.callback_off = callback_off

        self.prev_value = self.OFF
        self.value = self.OFF
        
        self.debounce_ms = BinarySensor.DEBOUNCE_MS

    def set_debounce(self, ms=20):
        """
        디바운스 시간을 설정합니다.

        :param ms: 디바운스 시간 (밀리초). 기본값은 20ms입니다.
        :type ms: int, optional
        """
        self.debounce_ms = ms

    def run(self):
        """
        버튼 상태를 업데이트하고 이벤트를 처리합니다.

        이 메서드는 자주 호출되어야 하며, 일반적으로 루프 내에서 사용됩니다.
        """
        self.prev_value = self.value
        self.value = self.pin.value()

        # OFF 상태가 유지되면 더 이상 처리하지 않음
        if self.prev_value == self.OFF and self.value == self.ON:
            time.sleep_ms(self.debounce_ms)
            if callable(self.callback_on):
                self.callback_on()
            
        elif self.prev_value == self.ON and self.value == self.OFF:
            time.sleep_ms(self.debounce_ms)
            if callable(self.callback_off):
                self.callback_off()

def pir_on():
    print('PIR on')
    
def pir_off():
    print('PIR off')
            
def main():
    import pinno as P
    from machine import Pin
    sensor = BinarySensor(pin_instance=Pin(P.PIR_IN,Pin.IN),inverted=False,callback_on=pir_on,callback_off=pir_off)
    
    while True:
        sensor.run()
        
if __name__ == '__main__':
    main()
    
    
