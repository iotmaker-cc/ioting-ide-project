# 리스트 생성
my_list = [10, 20, 30, 40]

# 리스트 요소에 접근 (인덱스는 0부터 시작)
print(my_list[0])  # 출력: 10
print(my_list[2])  # 출력: 30

# 리스트에 요소 추가
my_list.append(50)
print(my_list)  # 출력: [10, 20, 30, 40, 50]

# 특정 위치에 요소 삽입
my_list.insert(1, 15)
print(my_list)  # 출력: [10, 15, 20, 30, 40, 50]

# 리스트에서 요소 삭제
my_list.remove(30)
print(my_list)  # 출력: [10, 15, 20, 40, 50] 

# 인덱스로 요소 삭제
del my_list[2]
print(my_list)  # 출력: [10, 15, 40, 50]

# 리스트 길이 구하기
print(len(my_list))  # 출력: 4

# 리스트의 모든 요소 반복
for item in my_list:
    print(item)

# 리스트 슬라이싱
sub_list = my_list[1:3]  # [부터:앞 까지]
print(sub_list)  # 출력: [15, 40]
