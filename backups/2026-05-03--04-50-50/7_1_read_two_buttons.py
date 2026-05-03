from machine import Pin
import time
import pinno as pinno

# 핀 번호 상수 설정
BUTTON_1_PIN = pinno.L3_IN  # 첫 번째 버튼(PULL_UP)
BUTTON_2_PIN = pinno.L4_IN  # 두 번째 버튼(PULL_DOWN)

# 버튼 설정
button_1 = Pin(BUTTON_1_PIN, Pin.IN, Pin.PULL_UP)   # PULL_UP 방식
button_2 = Pin(BUTTON_2_PIN, Pin.IN, Pin.PULL_DOWN) # PULL_DOWN 방식

# 시작 메시지 출력
print("버튼_1과 버튼_2를 눌러 보셔요")

# 각 버튼의 이전 상태 저장
prev_button_1_state = button_1.value()
prev_button_2_state = button_2.value()

# 메인 루프
while True:
    # 버튼_1 상태 확인
    current_button_1_state = button_1.value()
    if current_button_1_state != prev_button_1_state: 
        print("버튼_1의 값이 바뀜", current_button_1_state)
        prev_button_1_state = current_button_1_state  # 상태 업데이트
        time.sleep(0.02)  # 디바운스 (20ms)

    # 버튼_2 상태 확인
    current_button_2_state = button_2.value()
    if current_button_2_state != prev_button_2_state:
        print("버튼_2의 값이 바뀜", current_button_2_state)
        prev_button_2_state = current_button_2_state  # 상태 업데이트
        time.sleep(0.02)  # 디바운스 (20ms)