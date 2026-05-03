"""
:input('입력 안내 문구'): 입력을 받아서 돌려줍니다.
:int(): 문자열을 숫자로 바꿉니다.
"""
temp = int(input('온도를 입력하세요... '))

if temp < 0:
    if temp < -10:
        msg = "온도가 매우 낮습니다."
    else:
        msg = "온도가 낮습니다."
else:
    if temp <= 30:
        if temp <= 20:
            msg = "온도가 적당합니다."
        else:
            msg = "온도가 높습니다."
    else:
        msg = "온도가 매우 높습니다."
        
print(f'{temp}도 이면 {msg}')