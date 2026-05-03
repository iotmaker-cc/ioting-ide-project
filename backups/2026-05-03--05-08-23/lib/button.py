"""
Button Class for MicroPython
version: 1.0(2024.09)
Copyright by: YANG Jaesam (iotmaker.cc@gmail.com)
All code is released under the MIT licence.
The author makes no warranties regarding this software.

file name: button.py
"""

from machine import Pin
import time

class Button:
    """
    MicroPython용 버튼 관리 클래스.

    `run()` 메서드는 자주 호출되어야 합니다.

    *** 예제 1
    ```python
    from machine import Pin
    from button import Button

    button = Button(Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP), inverted=True)

    def button_resp(response):
        print(f"{response['event_name']:<8}, clicks:{response['clicks']}, number:{response['number']}")

    button.add(Button.PRESSED, callback=button_resp)

    while True:
        button.run()
    ```

    *** 예제 2
    ```python
    from machine import Pin, Timer
    from button import Button
    from timerrun import TimerRun

    button = Button(Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP), inverted=True)

    def button_resp(response):
        print(f"{response['event_name']:<8}, clicks:{response['clicks']}, number:{response['number']}")

    button.add(Button.PRESSED, callback=button_resp)

    timerrun = TimerRun(Timer(0), period=10)
    timerrun.add(button.run())

    while True:
        pass
    ```
    """
    PULL_UP = Pin.PULL_UP
    PULL_DOWN = Pin.PULL_DOWN

    # 이벤트 타입
    PRESSED  = 0
    RELEASED = 1
    LONG     = 2
    SINGLE   = 3
    DOUBLE   = 4
    TRIPLE   = 5
    MULTIPLE = 6
    COUNT    = 7

    # 이벤트 이름
    event_name = [
        "PRESSED",
        "RELEASED",
        "LONG",
        "SINGLE",
        "DOUBLE",
        "TRIPLE",
        "MULTIPLE",
        "COUNT"
    ]

    def __init__(self,pin_instance, pull=-1,*,inverted=True, click_ms=500, long_ms=1500):
        """
        Button 클래스의 생성자.

        :param pin: 버튼에 연결된 Pin 객체.
        :type pin: machine.Pin
        :param inverted: 버튼 신호의 반전 여부. 기본값은 True입니다.
        :type inverted: bool, optional
        :param click_ms: 클릭으로 인식하기 위한 시간 임계값 (밀리초). 기본값은 500ms입니다.
        :type click_ms: int, optional
        :param long_ms: 롱 프레스으로 인식하기 위한 시간 임계값 (밀리초). 기본값은 1500ms입니다.
        :type long_ms: int, optional
        """
        # 인수
        if isinstance(pin_instance,Pin):
            self.pin = pin_instance
            if pull == Pin.PULL_UP:
                self.inverted = True
            elif pull == Pin.PULL_DOWN:
                self.inverted = False
            else:
                self.inverted = inverted
                
        elif isinstance(pin_instance,int):            
            self.pin = Pin(pin_instance,Pin.IN,pull)            
            if pull == Pin.PULL_UP:
                self.inverted = True
            elif pull == Pin.PULL_DOWN:
                self.inverted = False
            else:
                self.inverted = inverted

        if self.inverted:
            self.ON = 0
        else:
            self.ON = 1
            
        self.OFF = not self.ON

        self.click_threshold = click_ms
        self.long_threshold = long_ms

        # 추가된 이벤트 타입을 위한 콜백 저장소
        self.event_callbacks = [None] * len(Button.event_name)
        self.events = [False] * len(Button.event_name)

        # COUNT 타입 이벤트를 위한 콜백 및 숫자 저장소
        self.count_callbacks = []
        self.count_numbers = []

        # 디바운스를 위한 시간 (밀리초)
        self.debounce_ms = 20

        # 버튼이 눌리거나 떼어진 시점의 시간
        self.pressed_ms = 0
        self.released_ms = 0

        self.more_on_than_threshold = False
        self.more_off_than_threshold = True

        self.long_called = False
        self.click_count = 0

        self.prev_value = self.OFF
        self.value = self.OFF

    def set_debounce(self, ms=20):
        """
        디바운스 시간을 설정합니다.

        :param ms: 디바운스 시간 (밀리초). 기본값은 20ms입니다.
        :type ms: int, optional
        """
        self.debounce_ms = ms

    def add(self, event, callback, number=0):
        """
        특정 이벤트에 대한 콜백 함수를 추가합니다.

        :param event: 이벤트 타입. Button 클래스의 상수를 사용합니다.
        :type event: int
        :param callback: 이벤트 발생 시 호출될 콜백 함수.
        :type callback: callable
        :param number: COUNT 이벤트의 경우, 특정 클릭 수를 지정합니다. 기본값은 0입니다.
        :type number: int, optional
        """
        self.events[event] = True
        if event == Button.COUNT:
            self.count_callbacks.append(callback)
            self.count_numbers.append(number if number > 0 else 1)
        else:
            self.event_callbacks[event] = callback

    def remove(self, event, number=None):
        """
        특정 이벤트에 대한 콜백 함수를 제거합니다.

        :param event: 이벤트 타입. Button 클래스의 상수를 사용합니다.
        :type event: int
        :param number: COUNT 이벤트의 경우, 제거할 특정 클릭 수를 지정합니다. 기본값은 None입니다.
        :type number: int, optional
        """
        if event == Button.COUNT:
            try:
                i = self.count_numbers.index(number)
                del self.count_numbers[i]
                del self.count_callbacks[i]
                if len(self.count_numbers) > 0:
                    self.events[event] = True
                else:
                    self.events[event] = False
            except ValueError:
                print(f"ValueError in Button.remove(): {number}은(는) 범위를 벗어났습니다.")
        else:
            self.events[event] = False
            self.event_callbacks[event] = None

    def print_events(self):
        """
        등록된 모든 이벤트를 출력합니다.
        """
        print("--- Events List")
        for i, event in enumerate(self.events):
            if event:
                if i == Button.COUNT:
                    number_str = ', number=' + str(self.count_numbers)
                else:
                    number_str = ''
                print(f"{i}: {Button.event_name[i]}{number_str}")

    def _valid_event_count(self, i) -> bool:
        """
        COUNT 이벤트가 유효한지 확인합니다.

        :param i: COUNT 콜백의 인덱스.
        :type i: int
        :return: 유효하면 True, 그렇지 않으면 False.
        :rtype: bool
        """
        if self.count_numbers[i] != self.click_count or \
           (self.long_called and self.count_numbers[i] == 1):
            return False
        else:
            return True

    def do_event_count(self, i):
        """
        COUNT 이벤트를 처리합니다.

        :param i: COUNT 콜백의 인덱스.
        :type i: int
        """
        if not self._valid_event_count(i):
            return

        response = {
            'event': Button.COUNT,
            'event_name': Button.event_name[Button.COUNT],
            'number': self.count_numbers[i],
            'clicks': self.click_count
        }
        self.count_callbacks[i](response)

    def valid_event(self, event) -> bool:
        """
        일반 이벤트가 유효한지 확인합니다.

        :param event: 이벤트 타입.
        :type event: int
        :return: 유효하면 True, 그렇지 않으면 False.
        :rtype: bool
        """
        if not self.events[event] or \
           (event == Button.SINGLE and self.click_count != 1) or \
           (event == Button.DOUBLE and self.click_count != 2) or \
           (event == Button.TRIPLE and self.click_count != 3) or \
           (self.long_called and event == Button.MULTIPLE) or \
           (self.long_called and event == Button.SINGLE and self.click_count == 1):
            return False
        else:
            return True

    def do_event(self, event):
        """
        일반 이벤트를 처리합니다.

        :param event: 이벤트 타입.
        :type event: int
        """
        if not self.valid_event(event):
            return

        if event == Button.LONG:
            self.long_called = True

        response = {
            'event': event,
            'event_name': Button.event_name[event],
            'number': None,
            'clicks': self.click_count
        }
        self.event_callbacks[event](response)

    def first_off_threshold_reached(self):
        """
        버튼이 OFF 상태로 유지된 시간이 클릭 임계값을 초과했는지 확인합니다.

        :return: 초과했으면 True, 그렇지 않으면 False.
        :rtype: bool
        """
        return time.ticks_diff(time.ticks_ms(), self.released_ms) > self.click_threshold

    def long_press_detected(self):
        """
        버튼이 LONG 임계값을 초과하여 눌려졌는지 확인합니다.

        :return: 초과했으면 True, 그렇지 않으면 False.
        :rtype: bool
        """
        return time.ticks_diff(time.ticks_ms(), self.pressed_ms) > self.long_threshold

    def run(self):
        """
        버튼 상태를 업데이트하고 이벤트를 처리합니다.

        이 메서드는 자주 호출되어야 하며, 일반적으로 루프 내에서 사용됩니다.
        """
        self.prev_value = self.value
        self.value = self.pin.value()

        # OFF 상태가 유지되면 더 이상 처리하지 않음
        if self.more_off_than_threshold and self.prev_value == self.OFF and self.value == self.OFF:
            return

        # ON 상태가 유지되면 더 이상 처리하지 않음
        if self.more_on_than_threshold and self.prev_value == self.ON and self.value == self.ON:
            return

        # OFF -> ON 전환
        if self.prev_value == self.OFF and self.value == self.ON:
            self.pressed_ms = time.ticks_ms()
            if self.more_off_than_threshold:
                self.click_count = 0
            self.click_count += 1
            self.do_event(Button.PRESSED)

            self.more_on_than_threshold = False
            self.more_off_than_threshold = False
            self.long_called = False

            time.sleep_ms(self.debounce_ms)

        # ON -> OFF 전환
        elif self.prev_value == self.ON and self.value == self.OFF:
            self.released_ms = time.ticks_ms()
            self.do_event(Button.RELEASED)

            self.more_off_than_threshold = False

            time.sleep_ms(self.debounce_ms)

        # ON 상태에서 LONG 임계값 초과
        elif self.prev_value == self.ON and self.value == self.ON and self.long_press_detected():
            self.more_on_than_threshold = True
            self.do_event(Button.LONG)

        # OFF 상태에서 CLICK 임계값 초과
        elif self.prev_value == self.OFF and self.value == self.OFF and self.first_off_threshold_reached():
            self.do_event(Button.SINGLE)
            self.do_event(Button.DOUBLE)
            self.do_event(Button.TRIPLE)
            self.do_event(Button.MULTIPLE)

            for i, callback in enumerate(self.count_callbacks):
                self._valid_event_count(i)

            self.more_on_than_threshold = False
            self.more_off_than_threshold = True
            self.long_called = False

        return

# 메인 프로그램일 때 실행되는 코드
if __name__ == '__main__':
    def button_resp_short(response):
        global cnt
        if response['event'] == Button.LONG:
            print("\n", end="")

        if response['event'] == Button.PRESSED:
            cnt += 1
            print("P:", end="")
        elif response['event'] == Button.RELEASED:
            print("R:")
        else:
            cnt += 1
            print(f"{cnt} {response['event_name']:<8}, clicks:{response['clicks']}, number:{response['number']}")

    def button_resp_full(response):
        global cnt
        cnt += 1
        print(f"{cnt} {response['event_name']:<8}, clicks:{response['clicks']}, number:{response['number']}")

    def button_resp(response):
        global resp_print_mode, SHORT, FULL

        if resp_print_mode == SHORT:
            button_resp_short(response)
        elif resp_print_mode == FULL:
            button_resp_full(response)

    from machine import Pin, Timer
    import time

    btn1 = Button(Pin(0,Pin.IN,Pin.PULL_UP),inverted=True)
    #btn1 = Button(0,inverted=True)

    cnt = 0

    SHORT = 0
    FULL = 1
    resp_print_mode = FULL  # 0: short, 1: full

    btn1.add(Button.PRESSED, callback=button_resp)
    btn1.add(Button.RELEASED, callback=button_resp)
    btn1.add(Button.LONG, callback=button_resp)
    btn1.add(Button.MULTIPLE, callback=button_resp)
    btn1.add(Button.SINGLE, callback=button_resp)
    btn1.add(Button.DOUBLE, callback=button_resp)
    btn1.add(Button.TRIPLE, callback=button_resp)
    btn1.add(Button.COUNT, callback=button_resp, number=1)
    btn1.add(Button.COUNT, callback=button_resp, number=2)
    btn1.add(Button.COUNT, callback=button_resp, number=3)
    btn1.add(Button.COUNT, callback=button_resp, number=5)
    btn1.print_events()
    btn1.remove(Button.COUNT, number=5)
    # btn1.remove(Button.DOUBLE)
    btn1.print_events()

    while True:
        btn1.run()
        pass
