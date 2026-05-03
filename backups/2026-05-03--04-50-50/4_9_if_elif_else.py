hour = 14  # 현재 시간 (24시간 형식)

if hour < 12:
    print("Good morning!")
elif hour < 18:
    print("Good afternoon!")
elif hour < 21:
    print("Good evening!")
else:
    print("Good night!")
