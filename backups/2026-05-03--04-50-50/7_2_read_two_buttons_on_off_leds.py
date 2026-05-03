from machine import Pin
import time
import pinno

# 핀 번호 상수 설정
BUTTON_1_PIN = pinno.L3_IN
BUTTON_2_PIN = pinno.L4_IN
LED_1_PIN = pinno.L5_IN
LED_2_PIN = pinno.L6_IN

# 버튼이 눌린 값 설정
BUTTON_1_PRESSED_VALUE = 0  # 버튼_1 눌림
BUTTON_2_PRESSED_VALUE = 1  # 버튼_2 눌림

# LED의 ON/OFF 값 설정
LED_1_ON_VALUE = 1   # 전류 소싱 방식으로 연결된 LED_1 ON
LED_1_OFF_VALUE = not LED_1_ON_VALUE
LED_2_ON_VALUE = 0   # 전류 싱킹 방식으로 연결된 LED_2 ON
LED_2_OFF_VALUE = not LED_2_ON_VALUE

# 핀 설정: LED는 출력, 버튼은 입력(PULL_UP, PULL_DOWN)
led_1 = Pin(LED_1_PIN, Pin.OUT)
led_2 = Pin(LED_2_PIN, Pin.OUT)
button_1 = Pin(BUTTON_1_PIN, Pin.IN, Pin.PULL_UP)
button_2 = Pin(BUTTON_2_PIN, Pin.IN, Pin.PULL_DOWN)

# 초기 LED 상태 설정: OFF
led_1.value(LED_1_OFF_VALUE)
led_2.value(LED_2_OFF_VALUE)

# 시작 메시지 출력
print("버튼_1을 누르면 on(), 버튼_2를 누르면 off()")

# 버튼 상태 추적
prev_BUTTON_1_state = button_1.value()
prev_BUTTON_2_state = button_2.value()

while True:
    # 현재 버튼 상태 읽기
    current_BUTTON_1_state = button_1.value()
    current_BUTTON_2_state = button_2.value()

    # 버튼_1이 눌렸는지 확인
    if current_BUTTON_1_state == BUTTON_1_PRESSED_VALUE and prev_BUTTON_1_state != current_BUTTON_1_state:
        # LED1, LED2 켜기
        led_1.value(LED_1_ON_VALUE)
        led_2.value(LED_2_ON_VALUE)
        print("버튼_1 누름, 두 LED on")
        time.sleep_ms(20)  # 디바운스 시간

    # 버튼_2가 눌렸는지 확인
    if current_BUTTON_2_state == BUTTON_2_PRESSED_VALUE and prev_BUTTON_2_state != current_BUTTON_2_state:
        # LED1, LED2 끄기
        led_1.value(LED_1_OFF_VALUE)
        led_2.value(LED_2_OFF_VALUE)
        print("버튼_2 누름, 두 LED off")
        time.sleep_ms(20)  # 디바운스 시간

    # 상태 갱신
    prev_BUTTON_1_state = current_BUTTON_1_state
    prev_BUTTON_2_state = current_BUTTON_2_state

    # CPU 사용량 줄이기 위해 1ms 중지
    time.sleep_ms(1)