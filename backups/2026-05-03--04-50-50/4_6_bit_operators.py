a = 132
b = 45

fmt0 = '{:<10}'
fmt1 = '0b{:08b} 0x{:02x} {:3}'
n = 30

print(fmt0.format('a'),        fmt1.format(a,a,a))
print(fmt0.format('b'),        fmt1.format(b,b,b))
print('-'*n)
print(fmt0.format('a & b'),    fmt1.format(a&b,a&b,a&b))
print('비트 AND: 둘다 1일 때 1 반환\n')

print(fmt0.format('a'),        fmt1.format(a,a,a))
print(fmt0.format('b'),        fmt1.format(b,b,b))
print('-'*n)
print(fmt0.format('a | b'),    fmt1.format(a|b,a|b,a|b))
print('비트 OR: 둘 중 하나가 1일 때 1 반환\n')

print(fmt0.format('a'),        fmt1.format(a,a,a))
print(fmt0.format('b'),        fmt1.format(b,b,b))
print('-'*n)
print(fmt0.format('a ^ b '),   fmt1.format(a^b,a^b,a^b))
print('비트 XOR: 서로 다르면 1 반환\n')

print(fmt0.format('a'),        fmt1.format(a,a,a))
print('-'*n)
print(fmt0.format('~a'),       fmt1.format(~a&0xFF,~a&0xFF,~a&0xFF))
print('비트 NOT: 비트 반전(8bit로 제한:~a&0xFF)\n')
 
print(fmt0.format('a'),        fmt1.format(a,a,a))
print('-'*n)
print(fmt0.format('a<<2'),     fmt1.format(a<<2&0xFF,a<<2&0xFF,a<<2&0xff))
print('왼쪽 시프트: 2bit 이동(8bit로 제한:a<<2&0xFF)\n')

print(fmt0.format('a'),        fmt1.format(a,a,a))
print('-'*n)
print(fmt0.format('a>>2'),     fmt1.format(a>>2,a>>2,a>>2))
print('오른쪽 시프트: 2bit 이동\n')

print('{}의 보수는 {}이고, {}의 보수는 {}입니다.'.format(a,~a,~a,~~a))
print('양수(x)의 보수: -(x+1), 음수(x)의 보수: -x-1\n')
