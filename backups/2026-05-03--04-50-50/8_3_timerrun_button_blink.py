from machine import Pin, Timer
import time
from timerrun import TimerRun
from button import Button
from blink import Blink
import pinno

# 핀 번호 상수 설정
BUTTON_1_PIN = pinno.L3_IN
BUTTON_2_PIN = pinno.L4_IN
LED_1_PIN = pinno.L5_IN
LED_2_PIN = pinno.L6_IN

# LED 설정
led_1 = Blink(Pin(LED_1_PIN,Pin.OUT), inverted=False)  # 전류 소싱
led_2 = Blink(Pin(LED_2_PIN,Pin.OUT), inverted=True)   # 전류 싱킹

# 버튼 설정
button_1 = Button(Pin(BUTTON_1_PIN,Pin.IN,Pin.PULL_UP), inverted=True)   # PULL_UP
button_2 = Button(Pin(BUTTON_2_PIN,Pin.IN,Pin.PULL_DOWN), inverted=False) # PULL_DOWN

# TimerRun 오브젝트 생성
run = TimerRun(Timer(0), period=10)

# 버튼_1의 눌린 수만큼 LED_1 점멸
def handle_button_1(response):
    if response['event'] == Button.MULTIPLE:
        clicks = response['clicks']
        print(f"버튼_1을 {clicks}번 눌렀습니다. LED_1이 {clicks}번 점멸합니다.")
        led_1.begin_blink(on=500, off=300, count=clicks)

# 버튼_2를 누르고 있을 때 LED_2 점멸, 떼면 꺼짐
def handle_button_2(response):
    if response['event'] == Button.PRESSED:
        print("버튼_2를 누르고 있습니다. LED_2가 빠르게 점멸합니다.")
        led_2.begin_blink(on=250, off=250, count=0)  # 무한 반복
    elif response['event'] == Button.RELEASED:
        print("버튼_2에서 손을 뗐습니다. LED_2가 꺼집니다.")
        led_2.off()

# 버튼 이벤트 등록
button_1.add(event=Button.MULTIPLE, callback=handle_button_1)  # 누른 횟수에 따라 LED_1 점멸
button_2.add(event=Button.PRESSED, callback=handle_button_2)   # 버튼_2를 누르면 LED_2 점멸
button_2.add(event=Button.RELEASED, callback=handle_button_2)  # 버튼_2에서 손을 떼면 LED_2 꺼짐

# TimerRun에 버튼과 LED 상태 주기적 확인 등록
run.add(button_1.run)
run.add(button_2.run)
run.add(led_1.run)
run.add(led_2.run)

# 프로그램 시작 메시지 출력
print("버튼_1을 누른 횟수만큼 LED_1이 점멸합니다")
print("버튼_2를 누르고 있으면 LED_2가 빠르게 점멸하고, 떼면 꺼집니다")

# TimerRun 시작
run.start()

# 메인 루프: 1ms 간격으로 주기적으로 상태 확인
while True:
    time.sleep_ms(1)