# 참 값
a = True

# 거짓 값
b = False

# 숫자에서 bool로 변환
c = bool(0)  # False (0만이 False)
d = bool(1)  # True (0외의 모든 숫자)
e = bool(-1) # True (0외의 모든 숫자)
f = bool(10) # True (0외의 모든 숫자)

print(a, b, c, d, e, f)  # 출력: True False False True True True
