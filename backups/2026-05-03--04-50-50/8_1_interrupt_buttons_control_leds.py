from machine import Pin
import time
import pinno

# 핀 번호 상수 설정
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

# LED_1 토글 함수 (디바운스 포함)
def led_1_toggle(pin):
    # LED_1 토글
    if led_1.value() == LED_1_ON_VALUE:
        led_1.value(LED_1_OFF_VALUE)
    else:
        led_1.value(LED_1_ON_VALUE)

    # IRQ 비활성화 (디바운스 처리)
    button_1.irq(handler=None)  # IRQ 비활성화
    time.sleep_ms(300)         # 300ms 대기
    button_1.irq(trigger=Pin.IRQ_FALLING, handler=led_1_toggle)  # IRQ 다시 활성화

# LED_2 on/off 함수
def led_2_on_off(pin):
    if button_2.value() == 1:  # 버튼_2가 눌렸을 때
        led_2.value(LED_2_ON_VALUE)
    else:  # 버튼_2가 해제되었을 때
        led_2.value(LED_2_OFF_VALUE)

# IRQ 설정: 버튼_1의 FALLING 엣지에서 led_1_toggle() 실행
button_1.irq(trigger=Pin.IRQ_FALLING, handler=led_1_toggle)

# IRQ 설정: 버튼_2의 RISING, FALLING에서 led_2_on_off() 실행
button_2.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=led_2_on_off)

# 프로그램 시작 시 메시지 출력
print("버튼_1을 누르면 LED_1 toggle(), 버튼_2를 누르면 LED_2 on() 떼면 off()")

# LED 초기 상태 off
led_1.value(LED_1_OFF_VALUE)
led_2.value(LED_2_OFF_VALUE)

# 메인 루프
while True:
    time.sleep_ms(1)