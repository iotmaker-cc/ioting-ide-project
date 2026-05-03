from machine import Pin
import time
import dht

class DHT22Sensor:
    """
    :param pin_gpio: GPIO 핀 번호를 받아서 DHT22 센서를 초기화
    :param ser: 센서의 고유 식별자 (시리얼 번호 등)
    """
    def __init__(self, pin_gpio, ser=None):
        # DHT22 모델 설정
        self._model = "DHT22"
        self._model_ser = f"{self._model}_{ser}" if ser else self._model
        self.pin_gpio = pin_gpio
        self.temp_unit = "C"
        self.sensor_instance = dht.DHT22(Pin(pin_gpio))
        self._key = ["Temperature", "Humidity"]
        self._value = [None, None]

    def read(self):
        try:
            # 센서 값 읽기
            self.sensor_instance.measure()
            temp = round(self.sensor_instance.temperature(), 1)  # 소수점 1자리로 설정
            hum = int(self.sensor_instance.humidity())           # 정수로 설정
            self._value = [temp, hum]
            return {
                "TempUnit": self.temp_unit,
                self._model_ser: {
                    self._key[0]: self._value[0],
                    self._key[1]: self._value[1]
                }
            }
        except Exception as e:
            print("Error reading from DHT22:", e)
            return None

def main():
    import pinno as P
    from parse import Parse

    sensor = DHT22Sensor(P.DHT, ser="001")  # 예시로 "001"을 ser에 입력
    while True:        
        data = sensor.read()
        print(data)
        p = Parse(data)
        print(f'name: {p.name}, {p.keys[0]}: {p.values[0]}, {p.keys[1]}: {p.values[1]}, TempUnit: {p.temp_unit}')

        time.sleep_ms(5000)

if __name__ == '__main__':
    main()
