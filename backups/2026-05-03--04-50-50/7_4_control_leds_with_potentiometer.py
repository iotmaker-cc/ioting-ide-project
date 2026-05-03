from machine import Pin, ADC, PWM
import time
import pinno

# 핀 번호 상수 설정
POTENTIOMETER_PIN = pinno.L2_IN
BUTTON_1_PIN = pinno.L3_IN
BUTTON_2_PIN = pinno.L4_IN
LED_1_PIN = pinno.L5_IN
LED_2_PIN = pinno.L6_IN

# 상수 설정
BUTTON_1_PRESSED_VALUE = 0
BUTTON_2_PRESSED_VALUE = 1
PWM_FREQ = 1000

# 핀 객체 설정
potentiometer = ADC(Pin(POTENTIOMETER_PIN))
potentiometer.atten(ADC.ATTN_11DB)  # 3.3V까지 읽을 수 있도록 설정
potentiometer.width(ADC.WIDTH_12BIT)  # 12비트 해상도 설정

BUTTON_1 = Pin(BUTTON_1_PIN, Pin.IN, Pin.PULL_UP)
BUTTON_2 = Pin(BUTTON_2_PIN, Pin.IN, Pin.PULL_DOWN)

led_1 = PWM(Pin(LED_1_PIN))
led_2 = PWM(Pin(LED_2_PIN))

# 초기 설정
led_1.freq(PWM_FREQ)
led_2.freq(PWM_FREQ)
led_on_off_state = False
prev_potentiometer = 0
prev_BUTTON_1_state = BUTTON_1.value()
prev_BUTTON_2_state = BUTTON_2.value()

# 초기 메시지 출력
print("버튼_1을 누르면 on(), 버튼_2를 누르면 off()")
print("불이 켜지면 너브를 돌려서 밝기를 조절하셔요")

# 두 LED를 끔
led_1.duty(0)
led_2.duty(1023)

while True:
    # 현재 포텐셔미터 값을 읽음
    current_potentiometer = potentiometer.read()
    potentiometer_percent = int(current_potentiometer / 4095 * 100)

    # 포텐셔미터 값이 2% 이상 변했는지 확인
    if abs(current_potentiometer - prev_potentiometer) > (4095 * 0.02):
        prev_potentiometer = current_potentiometer

        # LED가 켜져 있을 때 밝기 조절
        if led_on_off_state:
            led_1_on_percent = potentiometer_percent
            led_2_on_percent = 100 - potentiometer_percent

            led_1.duty(int(led_1_on_percent / 100 * 1023))
            led_2.duty(int(led_2_on_percent / 100 * 1023))

            print(f"밝기 조절: {led_1_on_percent}%")

    # 버튼 상태 확인
    current_BUTTON_1_state = BUTTON_1.value()
    current_BUTTON_2_state = BUTTON_2.value()

    # 버튼 상태가 변경되었는지 확인 (디바운스 적용)
    if current_BUTTON_1_state != prev_BUTTON_1_state or current_BUTTON_2_state != prev_BUTTON_2_state:
        time.sleep_ms(20)  # 디바운스 시간

        # 버튼_1이 눌렸을 때
        if BUTTON_1.value() == BUTTON_1_PRESSED_VALUE:
            led_on_off_state = True
            led_1.duty(int(potentiometer_percent / 100 * 1023))
            led_2.duty(int((100 - potentiometer_percent) / 100 * 1023))
            print(f"on(): {potentiometer_percent}%")

        # 버튼_2가 눌렸을 때
        if BUTTON_2.value() == BUTTON_2_PRESSED_VALUE:
            led_on_off_state = False
            led_1.duty(0)
            led_2.duty(1023)
            print("off()")

    # 이전 버튼 상태 업데이트
    prev_BUTTON_1_state = current_BUTTON_1_state
    prev_BUTTON_2_state = current_BUTTON_2_state

    # 1ms 중지
    time.sleep_ms(1)