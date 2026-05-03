from machine import Pin, Timer
import time
import pinno

# 핀 설정
BUTTON_1_PIN = pinno.L3_IN
BUTTON_2_PIN = pinno.L4_IN
LED_1_PIN = pinno.L5_IN
LED_2_PIN = pinno.L6_IN

# LED 상태 값 설정
LED_1_ON_VALUE = 1
LED_1_OFF_VALUE = not LED_1_ON_VALUE
LED_2_ON_VALUE = 0
LED_2_OFF_VALUE = not LED_2_ON_VALUE

# LED 핀 설정
led_1 = Pin(LED_1_PIN, Pin.OUT)
led_2 = Pin(LED_2_PIN, Pin.OUT)

# 버튼 핀 설정
button_1 = Pin(BUTTON_1_PIN, Pin.IN, Pin.PULL_UP)
button_2 = Pin(BUTTON_2_PIN, Pin.IN, Pin.PULL_DOWN)

# 변수 설정
LED_1_blink_active = False
LED_1_timer = Timer(0)
LED_2_timer = Timer(1)

# LED_1 토글 함수 (0.5초 간격)
def led_1_blink(timer):
    led_1.value(not led_1.value())

# LED_2 토글 함수 (0.25초 간격)
def led_2_blink(timer):
    led_2.value(not led_2.value())

# 버튼_1 눌렀을 때 모드 변경
def button_1_mode_change(pin):
    global LED_1_blink_active
    LED_1_blink_active = not LED_1_blink_active

    if LED_1_blink_active:
        led_1.value(LED_1_ON_VALUE)  # LED_1 켜기
        # 0.5초 간격으로 LED_1 점멸
        LED_1_timer.init(period=500, mode=Timer.PERIODIC, callback=led_1_blink)
    else:
        # LED_1 타이머 해제 및 LED_1 끔
        LED_1_timer.deinit()
        led_1.value(LED_1_OFF_VALUE)

    # 디바운스 처리 (IRQ 해제 후 300ms 대기)
    button_1.irq(handler=None)  # IRQ 해제
    time.sleep_ms(300)         # 300ms 대기
    button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_1_mode_change)  # IRQ 다시 설정

# 버튼_2 눌렀을 때 LED_2 점멸 제어
def button_2_blink_or_not(pin):
    if button_2.value() == 1:  # 버튼_2가 눌린 상태
        led_2.value(LED_2_ON_VALUE)  # LED_2 켜기
        LED_2_timer.init(period=250, mode=Timer.PERIODIC, callback=led_2_blink)  # 0.25초 간격 LED_2 점멸
    else:  # 버튼_2가 해제된 상태
        LED_2_timer.deinit()
        led_2.value(LED_2_OFF_VALUE)  # LED_2 끔

# IRQ 설정
button_1.irq(trigger=Pin.IRQ_FALLING, handler=button_1_mode_change)
button_2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=button_2_blink_or_not)

# 프로그램 시작 메시지 출력 및 LED 초기화
print("버튼_1과 버튼_2를 각각 눌러서 두 LED의 점멸을 확인하셔요")
led_1.value(LED_1_OFF_VALUE)
led_2.value(LED_2_OFF_VALUE)

# 메인 루프
while True:
    pass

# 버튼_1은 LED_1의 점멸을 토글함.버튼_2를 누르는 동안 LED_2 점멸함.