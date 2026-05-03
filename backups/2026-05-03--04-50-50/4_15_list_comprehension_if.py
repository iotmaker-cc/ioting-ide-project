# for문을 이용하여 리스트 만들기(짝수일 때)
numbers_1 = []
for i in range(10):
    if i % 2 == 0: 
        numbers_1.append(i**2)

# 리스트 컴프리헨션을 이용하여 리스트 만들기(짝수일 때)
numbers_2 = [i**2 for i in range(10) if i % 2 == 0]

print(1,numbers_1)
print(2,numbers_2)