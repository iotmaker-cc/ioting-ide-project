from machine import ADC, Pin
import time
import pinno

# 핀 번호 상수 설정
POTENTIOMETER_PIN = pinno.L2_IN

# ADC 설정: 포텐셔미터 입력 핀을 ADC로 사용
potentiometer = ADC(Pin(POTENTIOMETER_PIN))

# ADC 분해능 설정 (기본 12비트, 최대 4095)
potentiometer.atten(ADC.ATTN_11DB)  # 최대 3.3V까지 측정 가능

# 퍼텐쇼미터 읽기 및 값 비교에 필요한 변수
prev_value = 0
first = True
THRESHOLD = 4095 * 0.005  # 0.5% 변화 임계값

# 프로그램 시작 메시지
print("퍼텐쇼미터의 노브를 돌려보세요.")

while True:
    # 퍼텐쇼미터 값 읽기
    current_value = potentiometer.read()
    
    # first가 True이거나, 값이 0.5% 이상 변했을 경우 출력
    if first or abs(current_value - prev_value) > THRESHOLD:
        # 4095에 대한 백분율 계산
        percentage = (current_value / 4095) * 100  
        print(f"퍼텐쇼미터 값: {current_value}, 백분율: {percentage:.2f}%")
        
        # 첫 번째 출력 후 first를 False로 설정
        first = False
        prev_value = current_value  # 이전 값 갱신

    # 1ms 대기
    time.sleep_ms(1)

    # 0.5초 간격으로 퍼텐쇼미터 값을 읽음
    time.sleep(0.5)