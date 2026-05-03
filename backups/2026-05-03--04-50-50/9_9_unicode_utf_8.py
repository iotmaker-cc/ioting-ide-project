# 함수 ord()는 문자의 유니코드 값을 나타냅니다.
uni_a = ord('a')
uni_han = ord('한')

byte_a = 'a'.encode('utf-8')
byte_han = bytearray('한'.encode('utf-8'))

# 각 바이트를 2진수로 변환하여 출력
binary_a   = ' '.join('{:08b}'.format(byte) for byte in byte_a)
binary_han = ' '.join('{:08b}'.format(byte) for byte in byte_han)

print()
print(f'유니코드 a: {uni_a:016b},\t한: {uni_han:016b}')
print()
print(f'utf-8   a: {binary_a}, \t\t한: {binary_han}')
print()

print(type(byte_han),byte_han)