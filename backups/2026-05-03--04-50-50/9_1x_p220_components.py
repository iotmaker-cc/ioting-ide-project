from machine import Pin
from run import Run
import pinno as P

run = Run()

from blink import Blink
led_1 = Blink(pin_instance=Pin(P.LED_1_IN, Pin.OUT), inverted=False)
run.add(led_1.run)

def led_toggle():
    led_1.toggle()

from timerrun import TimerRun
timer_led = TimerRun(period=1 * 1000, callback=led_toggle)
run.add(timer_led.run)

def main():
    while True:
        run.run()

if __name__ == '__main__':
    main()
