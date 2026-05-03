import network
import time

# Wi-Fi 설정 정보
SSID = 'your_ssid'
SSID_PASS = 'your_password'

# Wi-Fi 연결 함수
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)  # STA 모드 활성화 (Station)
    wlan.active(True)  # Wi-Fi 기능 켜기
    wlan.connect(SSID, SSID_PASS)  # Wi-Fi 네트워크에 연결

    # 연결 완료될 때까지 대기
    while not wlan.isconnected():
        print('Wi-Fi 연결 중...')
        time.sleep(1)

    # 연결 완료 시 IP 정보 출력
    print('Wi-Fi 연결 완료:', wlan.ifconfig())

# 프로그램 실행
connect_wifi()