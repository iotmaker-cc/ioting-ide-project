# 두 집합 정의
set1 = {1, 2, 3,'a'}
set2 = {3, 4, 5,'b'}

# 합집합
union_set = set1 | set2

# 교집합
intersection_set = set1 & set2

# 차집합
difference_set = set1 - set2

# 대칭 차집합
symmetric_difference_set = set1 ^ set2 # union_set - intersection_set

print('union',union_set)
print('intersection',intersection_set)
print('difference',difference_set)
print('symmetric_difference',symmetric_difference_set)