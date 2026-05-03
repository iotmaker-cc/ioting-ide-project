import machine
import pinno as P

# [1] I2C 초기화
# 예: ESP32에서 scl=22, sda=21인 경우 (I2C(1, ...) 대신 I2C(0, ...)를 사용할 수도 있음)
i2c = machine.I2C(0, scl=machine.Pin(P.SCL), sda=machine.Pin(P.SDA), freq=100000)

# DS1307 기본 I2C 주소
DS1307_I2C_ADDR = 0x68

# [2] 10진수 -> BCD 변환 함수
def dec_to_bcd(value):
    """예: 12 -> 0x12,  45 -> 0x45 형식 (2자리 10진수를 한 바이트로)"""
    return ((value // 10) << 4) + (value % 10)

# [3] DS1307의 시간/날짜 레지스터 세팅 함수
def ds1307_set_time(year, month, day, weekday, hour, minute, second):
    """
    year: 2000년 기준 offset (예: 2023년이면 23)
    month: 1~12
    day: 날짜(1~31)
    weekday: 요일(1~7). 요일 체계는 사용처에 따라 다를 수 있음.
    hour, minute, second: 24시간 형식
    """
    # DS1307 레지스터: 0=초, 1=분, 2=시, 3=요일, 4=일, 5=월, 6=년
    # seconds 레지스터(0번)의 상위 비트(CLock Halt)가 0이어야 동작
    # 여기서는 CH=0 상태로 second 세팅
    sec_reg = dec_to_bcd(second) & 0x7F  # bit7 = 0 (Clock Run)

    data = bytes([
        sec_reg,                 # 0번: Seconds (CH=0)
        dec_to_bcd(minute),      # 1번: Minutes
        dec_to_bcd(hour),        # 2번: Hours (24시간 모드 가정)
        dec_to_bcd(weekday),     # 3번: Day(요일)
        dec_to_bcd(day),         # 4번: Date(일)
        dec_to_bcd(month),       # 5번: Month
        dec_to_bcd(year)         # 6번: Year (00~99, 2000년부터)
    ])

    # [4] writeto_mem을 사용해 DS1307 레지스터 0번부터 순서대로 쓰기
    i2c.writeto_mem(DS1307_I2C_ADDR, 0, data)

# [5] 실제 시각 설정 예시
# 2025년 1월 9일 (화요일), 16시 10분 0초로 설정
ds1307_set_time(
    year=25,      # 2023년 -> 23 (2000 + 23)
    month=1,
    day=8,
    weekday=3,    # 예: 월=1, 화=2, 수=3, 목=4, 금=5, 토=6, 일=7
    hour=22,
    minute=33,
    second=0
)

print("DS1307에 초기 시간 값을 설정했습니다.")
