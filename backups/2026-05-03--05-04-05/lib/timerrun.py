#
# TimerRun Class for MicroPython
# version: 1.0(2024.09)
# Copyright by: YANG Jaesam (iotmaker.cc@gmail.com)
# All code is released under the MIT licence.
# The author makes no warranties regarding this software.
#

# timerrun.py

from machine import Timer
import time

class TimerRun:
    """
    MicroPython용 타이머 관리 클래스.

    :param timer: 사용할 machine.Timer 인스턴스. None일 경우 소프트웨어 모드로 작동합니다.
    :type timer: machine.Timer 또는 None
    :param period: 타이머 주기 (밀리초 단위). 기본값은 10,000 ms입니다.
    :type period: int, optional
    """

    DEFAULT_PERIOD = 10*1000

    def __init__(self, timer=None, period=None, callback=None):
        self.timer = timer
        self.timer_mode = True if self.timer else False

        self.period = period if period else TimerRun.DEFAULT_PERIOD

        self.callbacks = []
        self.add_count = 0
        if callback != None:
            if callable(callback):
                self.add_count += 1
                self.callbacks.append(callback)
            
            else:
                print('timerrun.init: Invalid callback=|{callback}|')       

        self.started = True

        if self.timer_mode:
            self.timer.init(period=self.period, mode=Timer.PERIODIC, callback=self._tick)

        self.start_ms = time.ticks_ms()
        self.is_on_state = False
        self.now_on_state = False

    def set(self, period=None):
        """
        타이머의 주기를 설정합니다.

        :param period: 새로운 주기 (밀리초 단위). None일 경우 기본 주기를 사용합니다.
        :type period: int 또는 None
        """
        self.period = period if period else TimerRun.DEFAULT_PERIOD

        if self.timer_mode:
            self.timer.init(period=self.period, mode=Timer.PERIODIC, callback=self._tick)
        else:
            self.start_ms = time.ticks_ms()

    def start(self):
        """
        타이머를 시작합니다.
        """
        self.started = True

    def stop(self):
        """
        타이머를 중지합니다.
        """
        self.started = False

    def add(self, callback):
        """
        타이머가 틱할 때 호출될 콜백 함수를 추가합니다.

        :param callback: 추가할 콜백 함수.
        :type callback: callable
        """
        if callable(callback):
            self.add_count += 1
            self.callbacks.append(callback)
#             print(f'timerrun.add(): add_count={self.add_count}')
        else:
            print('timerrun.add(): Invalid Function')
            
#         self.add_count += 1
#         self.callbacks.append(callback)

    def remove(self, callback):
        """
        등록된 콜백 함수를 제거합니다.

        :param callback: 제거할 콜백 함수.
        :type callback: callable
        """
        try:
            self.callbacks.remove(callback)
            self.add_count -= 1
        except ValueError:
            print("TimerRun.remove(): 아이템을 찾을 수 없습니다!")

    def now_on(self) -> None:
        """
        타이머를 즉시 트리거합니다.

        타이머를 시작 상태로 설정하고 콜백을 즉시 호출합니다.
        """
        self.started = True
        self.now_on_state = True
        if self.timer_mode:
            self._tick()
            self.timer.init(period=self.period, mode=Timer.PERIODIC, callback=self._tick)

    def is_on(self) -> bool:
        """
        타이머가 활성 상태인지 확인합니다.

        타이머 모드가 아닐 때만 유효합니다.

        :return: 타이머 이벤트가 발생했으면 True, 그렇지 않으면 False.
        :rtype: bool
        """
        if self.timer_mode:
            return
        if self.is_on_state:
            self.is_on_state = False
            return True
        else:
            return False

    def _tick(self, timer):
        """
        타이머 틱 시 호출되는 내부 메서드.

        등록된 모든 콜백 함수를 실행합니다.

        :param timer: 틱을 발생시킨 타이머 인스턴스.
        :type timer: machine.Timer
        """
        if not self.started or not self.timer_mode:
            return

        for callback in self.callbacks:
            callback()

    def run(self):
        """
        소프트웨어 모드에서 타이머를 실행합니다.

        이 메서드는 while True 루프 내에서 호출되어야 합니다.
        """
        if not self.started or self.timer_mode:
            return

        if self.now_on_state or time.ticks_diff(time.ticks_ms(), self.start_ms) > self.period:
            self.now_on_state = False
            self.is_on_state = True
            for callback in self.callbacks:
                callback()
            self.start_ms = time.ticks_ms()

ser = 0

def main():
    """
    TimerRun 사용 예제를 보여주는 메인 함수.

    두 개의 타이머를 설정합니다:
    - timer_seq: 각 틱마다 주기를 500 ms와 2000 ms 사이에서 변경합니다.
    - timer_char: 1000 ms마다 '*' 문자를 출력합니다. 호출 주기는 timer_seq에 의해  바뀝니다.
    """
    def func_timer_seq():
        global ser

        p = [500, 2000]

        print(f'type(timer_char): {type(timer_char)}')
        timer_char.set(period=p[ser])

        print(f'func_timer_seq > ser: {ser}, period: {p[ser]}')
        ser = (ser + 1) if ser < 1 else 0

    def func_timer_char():
        print('*')

    timer_seq = TimerRun(period=5*1000)
    timer_seq.add(func_timer_seq)
    timer_seq.now_on()

    timer_char = TimerRun(Timer(1), period=1*1000)
    timer_char.add(func_timer_char)

    while True:
        timer_seq.run()

if __name__ == '__main__':
    main()
