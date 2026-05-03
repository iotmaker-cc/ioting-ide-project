import network
import time
import ntptime
from machine import Pin, I2C
import pinno as P  # (문제에서 주어진 가상의 라이브러리: SDA_PIN, SCL_PIN 등이 있다고 가정)

'''
# [사용자 설정값들]
WIFI_SSID = "your_ssid"
WIFI_PASSWORD = "your_password"
'''
import config as C
WIFI_SSID = C.SSID
WIFI_PASSWORD = C.SSID_PASS

SDA_PIN = P.SDA       # 예: 21번 핀
SCL_PIN = P.SCL       # 예: 22번 핀
TIME_ZONE = +9        # 한국 KST는 UTC+9
NTP_SERVER = "pool.ntp.org"  # 사용할 NTP 서버 주소

# DS1307 기본 I2C 주소
DS1307_I2C_ADDR = 0x68

# BCD 변환 함수들
def bcd2dec(bcd):
    """
    BCD(Binary Coded Decimal)로 표현된 값을 10진수 정수로 변환.
    예: 0x12 -> 18
    """
    return ((bcd >> 4) * 10) + (bcd & 0x0F)

def dec2bcd(dec):
    """
    10진수 정수를 BCD(Binary Coded Decimal) 형태로 변환.
    예: 18 -> 0x12
    """
    return ((dec // 10) << 4) + (dec % 10)

class DS1307:
    """
    DS1307 외부 RTC를 I2C를 통해 직접 제어하기 위한 클래스.
    레지스터 0~6: 초,분,시,요일,일,월,년도(2자리)
    """
    def __init__(self, i2c, address=DS1307_I2C_ADDR):
        self.i2c = i2c
        self.address = address

    def set_datetime(self, year, month, day, weekday, hour, minute, second):
        """
        DS1307 레지스터에 날짜/시간을 써넣는다.
        - year: 4자리 연도 (예: 2025)
        - month: 1 ~ 12
        - day: 1 ~ 31
        - weekday: 1=월, 2=화, 3=수, 4=목, 5=금, 6=토, 7=일
        - hour, minute, second: 시/분/초 (24시간 형식)
        """
        # DS1307은 내부적으로 2자리 연도만 저장 (20xx)
        year_2digit = year % 100

        # 레지스터 순서대로 초, 분, 시, 요일, 일, 월, 연도
        data = bytearray(7)
        data[0] = dec2bcd(second) & 0x7F  # CH(bit7)는 0으로: DS1307 동작
        data[1] = dec2bcd(minute)
        data[2] = dec2bcd(hour)          # 24시간 모드
        data[3] = dec2bcd(weekday)       # 1=월 ~ 7=일
        data[4] = dec2bcd(day)
        data[5] = dec2bcd(month)
        data[6] = dec2bcd(year_2digit)

        # 0x00(첫 번째 레지스터)부터 7바이트 연속 써주기
        self.i2c.writeto_mem(self.address, 0x00, data)

    def get_datetime(self):
        """
        DS1307에서 현재 날짜/시간을 읽어 반환.
        반환값: (year, month, day, weekday, hour, minute, second)
        """
        data = self.i2c.readfrom_mem(self.address, 0x00, 7)
        second = bcd2dec(data[0] & 0x7F)  # bit7(CH)는 제외
        minute = bcd2dec(data[1])
        hour   = bcd2dec(data[2] & 0x3F) # 24시간 모드
        weekday= bcd2dec(data[3])        # 1=월 ~ 7=일
        day    = bcd2dec(data[4])
        month  = bcd2dec(data[5])
        year_2digit = bcd2dec(data[6])
        year   = 2000 + year_2digit      # DS1307은 20xx만 저장 가능
        return (year, month, day, weekday, hour, minute, second)

def connect_wifi(ssid, password):
    """
    주어진 SSID, PASSWORD로 와이파이에 연결.
    연결 완료되면 네트워크 정보(IP, 서브넷, 게이트웨이 등) 확인 가능.
    """
    print("[1/4] 와이파이 연결 중...")

    # 1) 스테이션 모드 활성화
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.active():
        sta_if.active(True)

    # 2) 연결 시도
    if not sta_if.isconnected():
        sta_if.connect(ssid, password)
        # 연결될 때까지 대기
        while not sta_if.isconnected():
            time.sleep(0.5)

    print("[1/4] 와이파이 연결 완료")
    return sta_if

def main():
    # 1) 와이파이 연결
    station = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    ip_info = station.ifconfig()
    print(f"[WiFi 정보] IP: {ip_info[0]}, Netmask: {ip_info[1]}, Gateway: {ip_info[2]}, DNS: {ip_info[3]}\n")

    # 2) NTP 서버 동기화
    print("[2/4] NTP 서버 설정 및 동기화 진행...")
    print(f"NTP 서버: {NTP_SERVER}")
    ntptime.host = NTP_SERVER
    ntptime.settime()  # 내부 RTC를 UTC로 세팅

    # 내부 RTC는 현재 UTC이므로, 로컬 타임(예: KST +9)을 위해 보정
    now = time.time() + TIME_ZONE * 3600
    local_time = time.localtime(now)
    # local_time 구조: (year, month, mday, hour, minute, second, weekday, yearday)

    # 3) I2C 초기화 후 DS1307에 시간 세팅
    print("[3/4] DS1307(RTC) 시간 세팅 중...")
    i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN), freq=100000)
    ds = DS1307(i2c)

    # MicroPython weekday(월=0, 화=1, 수=2, 목=3, 금=4, 토=5, 일=6) -> DS1307(1~7)
    ds1307_wday = local_time[6] + 1
    if ds1307_wday > 7:
        ds1307_wday = 7

    year, month, day = local_time[0], local_time[1], local_time[2]
    hour, minute, second = local_time[3], local_time[4], local_time[5]

    ds.set_datetime(year, month, day, ds1307_wday, hour, minute, second)

    # 설정된 시간 출력
    weekday_kor = ["월", "화", "수", "목", "금", "토", "일"]
    print("[세팅된 날짜/시간 정보]")
    print(f" {year}년 {month}월 {day}일 ({weekday_kor[ds1307_wday - 1]}) {hour:02d}:{minute:02d}:{second:02d}\n")

    # 4) 5초 후 DS1307에서 시간 읽어오기
    print("[4/4] 5초 대기 후 DS1307 다시 읽어오기...")
    time.sleep(5)
    year_r, month_r, day_r, wday_r, hour_r, min_r, sec_r = ds.get_datetime()

    # 읽어온 시간 출력
    print("[읽어온 날짜/시간 정보]")
    print(f" {year_r}년 {month_r}월 {day_r}일 ({weekday_kor[wday_r - 1]}) {hour_r:02d}:{min_r:02d}:{sec_r:02d}\n")

if __name__ == "__main__":
    main()
    
    
    
    