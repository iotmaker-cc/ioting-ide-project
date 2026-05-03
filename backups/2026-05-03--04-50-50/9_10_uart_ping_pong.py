from machine import UART
import pinno as P
import time
import json

# UART 초기화
uart1 = UART(1, baudrate=9600, tx=P.TX, rx=P.RX, timeout=10)
uart2 = UART(2, baudrate=9600, tx=P.R5, rx=P.R6, timeout=10)

def main():
    # 초기 데이터 전송
    data = {'ser': 1}
    uart1.write(json.dumps(data) + '\n')  # 데이터를 JSON 문자열로 전송
    print(f"UART1 sent: {data}")

    while True:
        # UART2에서 데이터 수신 및 처리
        if uart2.any():  # UART2에 수신된 데이터가 있으면
            received = uart2.readline()  # 데이터를 줄 단위로 읽기
            try:
                received_data = json.loads(received.decode().strip())  # JSON 디코드
                print(f"UART2 received: {received_data}")

                # ser 값 증가 및 출력
                received_data['ser'] += 1
                print(f"UART2 sending: {received_data}")

                # 5초 대기 후 UART1로 전송
                time.sleep(5)
                uart2.write(json.dumps(received_data) + '\n')
            except Exception as e:
                print(f"Error processing UART2 data: {e}")

        # UART1에서 데이터 수신 및 처리
        if uart1.any():  # UART1에 수신된 데이터가 있으면
            received = uart1.readline()  # 데이터를 줄 단위로 읽기
            try:
                received_data = json.loads(received.decode().strip())  # JSON 디코드
                print(f"UART1 received: {received_data}")

                # ser 값 증가 및 출력
                received_data['ser'] += 1
                print(f"UART1 sending: {received_data}")

                # 5초 대기 후 UART2로 전송
                time.sleep(5)
                uart1.write(json.dumps(received_data) + '\n')
            except Exception as e:
                print(f"Error processing UART1 data: {e}")

if __name__ == "__main__":
    main()
