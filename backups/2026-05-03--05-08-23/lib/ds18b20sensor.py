from machine import Pin
import time
import onewire
import ds18x20
import binascii

# file: ds18b20sensor.py
class DS18B20Sensor:
    """
    DS18B20 온도 센서 클래스.
    
    :param pin_gpio: DS18B20 센서를 연결할 GPIO 핀을 지정합니다.
    :param ser: 센서의 고유 식별자 (선택 사항)
    """

    def __init__(self, *, pin_gpio: int, ser=None) -> None:
        """
        DS18B20 센서를 초기화합니다.

        :param pin_gpio: DS18B20 센서를 연결할 GPIO 핀
        :param ser: 센서의 고유 식별자 (선택 사항)
        """
        # pin_gpio를 사용해 Pin 인스턴스를 만듭니다.
        self.pin_or_bus = Pin(pin_gpio, Pin.IN)

        # OneWire 인스턴스 생성
        self.ow = onewire.OneWire(self.pin_or_bus)
        
        # DS18X20 센서 인스턴스 생성
        self.sensor_instance = ds18x20.DS18X20(self.ow)

        # 센서 모델 설정
        self._model = 'DS18B20'
        self._model_ser = f"{self._model}_{ser}" if ser else self._model

        # 센서 데이터 초기화
        self._sensor_id = self.ow.scan()  # OneWire 버스에 연결된 센서 주소 리스트
        self._sensor_count = len(self._sensor_id)  # 연결된 센서의 수

        # 디버깅: 감지된 센서의 주소를 출력합니다.
        print(f"Detected DS18B20 sensors:{[b.hex() for b in self._sensor_id]}")

        self._names = []
        self.name_first = True
        self._keys = ['Temperature']  # 첫 번째 key는 'Temperature'
        self._values = []  # 센서에서 읽은 값
        self._sensor_id_hex = []  # DS18B20 센서의 고유 ID HEX 값
        self._dict = {}  # 센서 데이터를 저장할 딕셔너리

        try:
            if self._sensor_count == 0:
                print("No DS18B20 sensors found!")
                self._values = [None]
            else:
                for sensor_id in self._sensor_id:
                    self._sensor_id_hex.append(self.hex_id(sensor_id))  # 센서의 HEX ID 생성
        except OSError as e:
            print("센서 연결 실패:", e)
            self._values = [None]  # 센서 연결 실패 시 값을 None으로 처리

    def make_data(self):
        """
        센서에서 데이터를 읽고 처리하는 함수입니다.
        """
        try:
            self.sensor_instance.convert_temp()  # 온도 변환 시작
            time.sleep_ms(750)  # DS18B20 센서의 온도 변환 시간 (750ms 대기)
            
            # 온도 읽기
            for sensor_id in self._sensor_id:
                temperature = self.sensor_instance.read_temp(sensor_id)
                self._values.append(round(temperature, 1))  # 소숫점 1자리로 반올림
        except OSError as e:
            self._values = [None]  # 오류 발생 시 None 처리

    def make_dict(self):
        """
        센서 데이터를 딕셔너리 형태로 변환하는 함수입니다.
        """
        if self._model == 'DS18B20':
            for i in range(self._sensor_count):
                sensor_data = {
                    "Id": self._sensor_id_hex[i],  # 센서 고유 ID
                    self._keys[0]: self._values[i]  # 'Temperature'에 해당하는 센서 값
                }
                this_name_ser = self._model_ser + f"_{i+1}" if self._sensor_count > 1 else self._model_ser
                self._dict[this_name_ser] = sensor_data
        else:
            sensor_data = {}
            for i in range(len(self._keys)):
                sensor_data[self._keys[i]] = self._values[i]
            self._dict[self._model_ser] = sensor_data

    def read(self):
        """
        센서 데이터를 읽고, 딕셔너리 형태로 반환합니다.
        """
        self._values = []
        self.make_data()  # 센서 데이터를 먼저 읽음
        self.make_dict()  # 데이터를 딕셔너리 형식으로 정리

        # 온도 단위 처리
        self._dict['TempUnit'] = 'C'  # 섭씨 단위로 설정 (기본값 C)

        return self._dict

    def hex_id(self, id):
        """
        센서의 고유 ID를 HEX 형식으로 변환합니다.
        """
        return binascii.hexlify(id).decode('utf-8')


def main():
    import pinno as P
    from parse import Parse

    # DS18B20 센서를 GPIO에 연결
#     sensor = DS18B20Sensor(pin_gpio=P.DS18B20_IN)
    sensor = DS18B20Sensor(pin_gpio=P.DS18B20_IN)           # L3,L4
    
    while True:
        data = sensor.read()  # 센서 데이터를 읽음
        print(data)  # 센서 데이터 출력

        p = Parse(data)  # Parse 객체를 사용하여 데이터 파싱
    
        # 파싱된 각 센서 정보를 출력
        for i in range(len(p.names)):
            print(f'name: {p.names[i]}, Id: {p.ow_ids[i]}, {p.ow_keys[i]}: {p.ow_values[i]}')

        time.sleep_ms(5000)  # 5초 대기 후 반복


if __name__ == '__main__':
    main()
