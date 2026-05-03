from machine import I2C, Pin
import time

class BH1750Sensor:
    """
    :param i2c_bus: I2C 버스를 사용하여 BH1750 센서를 초기화
    :param ser: 센서의 고유 식별자 (옵션)
    """
    def __init__(self, i2c_bus, ser=None) -> None:
        self.pin_or_bus = i2c_bus
        self.sensor_instance = i2c_bus  # i2c_bus 인스턴스 사용
        self.address = 0x23  # BH1750 기본 주소
        self._model: str = "BH1750"
        self._model_ser: str = f"{self._model}_{ser}" if ser else self._model
        self._sensor_count: int = 1  # BH1750은 하나의 센서로 동작
        self._names: list[str] = []
        self.name_first = True
        self._key: list[str] = ["Brightness"]
        self._value: list[any] = [None]
        self._dict = {}

        try:
            # 센서 초기화: 연속 고해상도 모드
            self.sensor_instance.writeto(self.address, b'\x10')
            time.sleep_ms(180)
        except OSError as e:
            print(f"오류: 장치 연결 실패 {e}")
            self._value = [None]

    def make_data(self):
        """
        센서 데이터를 읽어와서 _value에 저장
        """
        try:
            # BH1750 데이터 읽기
            data = self.sensor_instance.readfrom(self.address, 2)
            brightness = (data[0] << 8 | data[1]) / 1.2  # 조도 값 계산 (1.2로 나누기)
            self._value[0] = round(brightness)  # 조도 값은 소수점 0자리로 처리
        except OSError as e:
            print(f"오류 발생: {e}")
            self._value = [None]

    def make_dict(self):
        """
        _value 리스트의 데이터를 _dict로 변환
        """
        sensor_data = {self._key[0]: self._value[0]}
        self._dict[self._model_ser] = sensor_data

    def read(self):
        """
        센서 데이터를 읽고, 딕셔너리 형태로 반환
        """
        self.make_data()  # 센서 데이터를 먼저 읽음
        self.make_dict()  # 데이터를 딕셔너리로 구성
        return self._dict

def main(): 
    import pinno as P 
    from parse import Parse

    i2c = I2C(0, scl=Pin(P.SCL), sda=Pin(P.SDA))

    sensor = BH1750Sensor(i2c_bus=i2c)
    while True:        
        data = sensor.read()
        print(data)
        p = Parse(data)
        print(f'name: {p.name}, {p.key}: {p.value}')   

        time.sleep_ms(5000)

if __name__ == '__main__':
    main()
