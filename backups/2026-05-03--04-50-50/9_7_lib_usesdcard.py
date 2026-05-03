# file: usesdcard.py
from machine import Pin, SPI
import os
import ujson
import sdcard
import time

class UseSDCard:
    """
    SD카드 사용을 위한 클래스

    :param spi_bus: SPI 버스 인스턴스
    :param cs_gpio: 칩 선택 핀 번호
    :param mount: 마운트 지점 (기본값 'sd')
    """
    def __init__(self, spi_bus, cs_gpio, mount='sd') -> None:
        # SPI 버스는 외부에서 인스턴스로 전달되므로 별도 생성 불필요
        self.spi_bus = spi_bus

        # 칩 선택 핀 설정
        self.cs_pin = Pin(cs_gpio)

        # 마운트 지점 경로
        self.mount_point = '/' + mount

        # 작업 중인 파일 변수
        self._file = None

    def mount_sdcard(self) -> tuple:
        """
        SD카드를 마운트함.
        
        :return: (성공 여부, 메시지)
        """
        try:
            # SDCard 인스턴스 생성 후 VFS 마운트
            sd = sdcard.SDCard(self.spi_bus, self.cs_pin)  # SDCard 인스턴스 생성
            vfs = os.VfsFat(sd)  # VFS 생성
            os.mount(vfs, self.mount_point)  # SD카드 마운트
            return True, 'SD card mounted successfully!'
        except Exception as e:
            return False, f'SD card mount failed: {str(e)}'

    def make_next_file(self, prefix: str, digits: int, ext: str) -> tuple:
        """
        새로운 파일을 생성함.
        
        :param prefix: 파일 이름의 접두사
        :param digits: 파일 번호 자릿수
        :param ext: 파일 확장자
        :return: (성공 여부, 메시지)
        """
        try:
            files = os.listdir(self.mount_point)
            max_ser = 0
            for f in files:
                if f.startswith(prefix) and f.endswith(f'.{ext}'):
                    ser_str = f[len(prefix):-len(ext)-1]
                    if ser_str.isdigit():
                        ser = int(ser_str)
                        max_ser = max(max_ser, ser)

            next_ser = (max_ser + 1) % (10 ** digits)
            file_name = f'{prefix}{next_ser:0{digits}}.{ext}'
            self._file = f'{self.mount_point}/{file_name}'

            with open(self._file, 'w') as f:
                f.write('')  # 빈 파일 초기화

            return True, 'File created successfully!'
        except Exception as e:
            return False, f'File creation failed: {str(e)}'

    def get_file(self) -> str:
        """
        현재 작업 중인 파일 경로를 반환함.
        
        :return: 파일 경로
        """
        return self._file

    def append_json(self, data_dictionary: dict) -> tuple:
        """
        데이터를 JSON 형식으로 파일에 추가함.
        
        :param data_dictionary: 추가할 데이터 딕셔너리
        :return: (성공 여부, 메시지)
        """
        try:
            with open(self._file, 'a') as f:
                json_str = ujson.dumps(data_dictionary) + '\n'
                f.write(json_str)
            return True, 'Data appended successfully!'
        except Exception as e:
            return False, f'Append failed: {str(e)}'

    def append_str(self, data_str: str) -> tuple:
        """
        문자열 데이터를 파일에 추가함.
        
        :param data_str: 추가할 문자열
        :return: (성공 여부, 메시지)
        """
        try:
            with open(self._file, 'a') as f:
                f.write(data_str + '\n')
            return True, 'String appended successfully!'
        except Exception as e:
            return False, f'Append failed: {str(e)}'

    def read(self) -> str:
        """
        파일의 내용을 읽어 반환함.
        
        :return: 파일의 내용
        """
        try:
            with open(self._file, 'r') as f:
                return f.read()
        except Exception as e:
            return f'Read failed: {str(e)}'

# 사용 예제
def main():
    from machine import Pin, SPI
    import time
    import pinno as P

    # 핀 번호 설정
    SCK_PIN = P.SCK
    MISO_PIN = P.MISO
    MOSI_PIN = P.MOSI
    CS_PIN = P.CS

    # SPI 버스 초기화
    spi_bus = SPI(1, baudrate=1000000, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN), miso=Pin(MISO_PIN))

    # UseSDCard 클래스 인스턴스 생성
    sd = UseSDCard(spi_bus, CS_PIN)

    # SD카드 마운트
    ok, message = sd.mount_sdcard()
    print(ok, message)

    # 새로운 파일 생성
    ok, message = sd.make_next_file(prefix='temphum', digits=3, ext='json')
    print(ok, message, sd.get_file())

    # 노랫말 생성
    song = [{'text': f'노랫말 {i}'} for i in range(5)]

    # SD카드에 노랫말 추가
    for s in song:
        ok, message = sd.append_json(s)
        print(ok, message)

    # 파일 내용 읽기
    file_data = sd.read()
    print(file_data)

if __name__ == '__main__':
    main()