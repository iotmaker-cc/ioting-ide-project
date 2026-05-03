#
# Blink Class for MicroPython
# version: 1.0(2024.09)
# Copyright by: YANG Jaesam (iotmaker.cc@gmail.com)
# All code is released under the MIT licence.
# The author makes no warranties regarding this software.
#

# blink.py
from machine import Pin

class Blink:
    """
    MicroPython용 LED 깜빡임 제어 클래스.

    이 클래스는 LED를 깜빡이거나 특정 이벤트 콜백을 호출하는 기능을 제공합니다.
    LED 핀을 제어하거나 함수 모드로 동작할 수 있습니다.
    """

    STR_ON = '*on*true*yes*y*1*'
    STR_OFF = '*off*false*no*n*0*'
    STR_TOGGLE = '*t*toggle*to*'

    import time

    def __init__(self, pin_instance=None,*,callback_on=None, callback_off=None, callback_end=None, inverted=False):
        """
        Blink 클래스의 생성자.

        :param pin_gpio: LED에 연결된 GPIO 핀 번호. None일 경우 함수 모드로 동작합니다.
        :type pin_gpio: int 또는 None, optional
        :param callback_on: LED가 켜질 때 호출될 콜백 함수.
        :type callback_on: callable, optional
        :param callback_off: LED가 꺼질 때 호출될 콜백 함수.
        :type callback_off: callable, optional
        :param callback_end: LED 깜빡임이 끝났을 때 호출될 콜백 함수.
        :type callback_end: callable, optional
        :param inverted: LED 신호의 반전 여부. 기본값은 False입니다.
        :type inverted: bool, optional
        """
        if pin_instance is None:
            self.led_mode = False
            self.led = None
            
        elif isinstance(pin_instance,Pin):
            self.led_mode = True
            self.led = pin_instance
                
        elif isinstance(pin_instance,int):
            self.led_mode = True
            self.led = Pin(pin_instance,Pin.OUT)

        self.func_mode = not self.led_mode

        self.callback_on = callback_on
        self.callback_off = callback_off
        self.callback_end = callback_end

        if inverted:
            self.ON = 0
        else:
            self.ON = 1
        self.OFF = not self.ON

        self.ON_DURATION = None
        self.OFF_DURATION = None
        self.COUNT = 0            # 반복 횟수
        self.counted = 0

        self.led_state = self.OFF
        self.duration = self.OFF_DURATION
        self.start_time = None

        self.blink_activated = False
        
        self.off()

    def set_callback(self, callback_on=None, callback_off=None, callback_end=None):
        """
        LED 상태 변화 시 호출될 콜백 함수를 설정합니다.

        :param callback_on: LED가 켜질 때 호출될 콜백 함수.
        :type callback_on: callable, optional
        :param callback_off: LED가 꺼질 때 호출될 콜백 함수.
        :type callback_off: callable, optional
        :param callback_end: LED 깜빡임이 끝났을 때 호출될 콜백 함수.
        :type callback_end: callable, optional
        """
        if callback_end:
            self.callback_end = callback_end

        if self.func_mode:
            if callback_on:
                self.callback_on = callback_on
            if callback_off:
                self.callback_off = callback_off

    def begin_blink(self, on=1000, off=500, count=0):
        """
        LED 깜빡임을 시작합니다.

        :param on: LED가 켜져 있을 시간 (밀리초). 기본값은 1000ms입니다.
        :type on: int, optional
        :param off: LED가 꺼져 있을 시간 (밀리초). 기본값은 500ms입니다.
        :type off: int, optional
        :param count: 깜빡임 반복 횟수. 0일 경우 무한 반복됩니다. 기본값은 0입니다.
        :type count: int, optional
        """
        self.blink_activated = True

        self.ON_DURATION = on if on > 0 else 1000
        self.OFF_DURATION = off if off > 0 else 500

        self.COUNT = count if count >= 0 else 0
        self.counted = 0

        self.led_state = self.ON
        self.duration = self.ON_DURATION

        self.start_time = Blink.time.ticks_ms()

        self.set_on_off(self.led_state)
        

    def end_blink(self):
        """
        LED 깜빡임을 종료하고 LED를 꺼집니다.
        """
        self.blink_activated = False

        self.led_state = self.OFF
        self.duration = self.OFF_DURATION

        self.start_time = Blink.time.ticks_ms()

        self.set_on_off(self.led_state)

    def on(self):
        """
        LED를 켭니다.
        """
        self.blink_activated = False

        self.led_state = self.ON
        self.set_on_off(self.led_state)

    def off(self):
        """
        LED를 끕니다.
        """
        self.blink_activated = False

        self.led_state = self.OFF
        self.set_on_off(self.led_state)

    def toggle(self):
        """
        LED 상태를 토글합니다. 켜져 있으면 끄고, 꺼져 있으면 켭니다.
        """
        if self.blink_activated:
            self.blink_activated = False
            self.led_state = self.OFF

        self.led_state = not self.led_state
        self.set_on_off(self.led_state)

    def is_blink_active(self) -> bool:
        """
        LED 깜빡임이 활성화되어 있는지 확인합니다.

        :return: 활성화되어 있으면 True, 아니면 False.
        :rtype: bool
        """
        return self.blink_activated

    def is_on(self) -> bool:
        """
        LED가 켜져 있는지 확인합니다.

        :return: 켜져 있으면 True, 아니면 False.
        :rtype: bool
        """
        return True if self.led_state == self.ON else False

    def on_off(self) -> str:
        """
        LED의 현재 상태를 문자열로 반환합니다.

        :return: 'on' 또는 'off' 문자열.
        :rtype: str
        """
        return 'on' if self.led_state == self.ON else 'off'

    def value(self):
        """
        LED의 현재 상태 값을 반환합니다.

        :return: LED 상태 값 (ON 또는 OFF).
        """
        return self.led_state

    def get_response(self) -> dict:
        """
        현재 LED 상태에 대한 정보를 딕셔너리 형태로 반환합니다.

        :return: LED 상태 정보 딕셔너리.
        :rtype: dict
        """
        return {
            'is_blink_active': self.is_blink_active(),
            'is_on': self.is_on(),
            'on_off': self.on_off()
        }

    def set_on_off(self, val):
        """
        LED의 상태를 설정하거나 콜백 함수를 호출합니다.

        :param val: 설정할 LED 상태 (ON 또는 OFF).
        :type val: int
        """
        if self.led_mode:
            self.led.value(val)
            return

        if self.callback_on is None or self.callback_off is None:
            return

        if val == self.ON:
            self.callback_on(self.get_response())
        elif val == self.OFF:
            self.callback_off(self.get_response())

    def set_on_off_str(self, in_val: str):
        """
        문자열 입력을 통해 LED 상태를 설정하거나 콜백 함수를 호출합니다.

        :param in_val: 'on', 'off', 또는 'toggle' 문자열.
        :type in_val: str
        """
        if self.led_mode:
            val = '*' + in_val.lower() + '*'
            if val in Blink.STR_ON:
                self.on()
            elif val in Blink.STR_OFF:
                self.off()
            elif val in Blink.STR_TOGGLE:
                self.toggle()
            return

        if self.callback_on is None or self.callback_off is None:
            return

        if in_val.lower() in ['on', 'true', 'yes', 'y', '1']:
            self.callback_on(self.get_response())
        elif in_val.lower() in ['off', 'false', 'no', 'n', '0']:
            self.callback_off(self.get_response())
        elif in_val.lower() in ['t', 'toggle', 'to']:
            self.toggle()

    def run(self):
        """
        LED 깜빡임을 관리합니다. 주기적으로 호출되어야 합니다.

        깜빡임이 활성화되어 있을 때, 지정된 시간에 따라 LED 상태를 전환합니다.
        반복 횟수가 지정되어 있으면 해당 횟수만큼 깜빡인 후 종료됩니다.
        """
        if not self.blink_activated:
            return

        if self.COUNT > 0 and self.counted >= self.COUNT:
            self.blink_activated = False
            if self.callback_end:
                self.callback_end(self.get_response())
            return

        if Blink.time.ticks_diff(Blink.time.ticks_ms(), self.start_time) >= self.duration:

            if self.led_state == self.ON:
                self.led_state = self.OFF
                self.duration = self.OFF_DURATION
                if self.COUNT > 0:
                    self.counted += 1

            else:
                self.led_state = self.ON
                self.duration = self.ON_DURATION

            self.set_on_off(self.led_state)
            self.start_time = Blink.time.ticks_ms()


def main_func():
    """
    Blink 클래스의 함수 모드를 사용하는 예제 함수.

    콜백 함수를 설정하고 LED를 깜빡이게 합니다.
    """
    def on_func(resp):
        print(f"on() \ton:{resp['is_on']},\tblink:{resp['is_blink_active']}")

    def on_func_new(resp):
        print(f"on_new() \ton:{resp['is_on']},\tblink:{resp['is_blink_active']}")

    def off_func(resp):
        print(f"off() \ton:{resp['is_on']},\tblink:{resp['is_blink_active']}")

    def end(resp):
        print(f"end() \ton:{resp['is_on']},\tblink:{resp['is_blink_active']}")

    from machine import Pin
    import time

    blink_func = Blink(callback_on=on_func, callback_off=off_func, callback_end=end)
    blink_func.off()
    blink_func.begin_blink(1000, 500, 5)

    while True:
        blink_func.run()
        pass


def main_led():
    """
    Blink 클래스를 LED 핀과 함께 사용하는 예제 함수.

    두 개의 LED를 제어하고 각각 다른 설정으로 깜빡이게 합니다.
    """
    def func_end(resp):
        led1.on()
        led2.on()
        print('end nof blinking led1')

    import pinno

    LED_1_PIN = pinno.L5_IN
    LED_2_PIN = pinno.L6_IN

    LED_1 = Pin(LED_1_PIN, Pin.OUT)
    LED_2 = Pin(LED_2_PIN, Pin.OUT)
    
    led1 = Blink(LED_1, inverted=False, callback_end=func_end)
    led2 = Blink(LED_2, inverted=True)

#     led1 = Blink(LED_1_PIN, inverted=False, callback_end=func_end)
#     led2 = Blink(LED_2_PIN, inverted=True)

    led1.off()
    led2.off()

    led1.begin_blink(500, 300, 10)
    led2.begin_blink(100, 100, 20)

    while True:
        led1.run()
        led2.run()


if __name__ == '__main__':
    #main_func()
    main_led()
