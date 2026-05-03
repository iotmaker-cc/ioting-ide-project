class Dog:
    # 클래스 생성자 (객체 초기화)
    def __init__(self, name, breed):
        self.name = name  # 속성 정의
        self.breed = breed  # 속성 정의
    
    # 메소드 정의
    def bark(self):
        print(f"{self.name} says woof!")

# 객체 생성
my_dog = Dog("Buddy", "Golden Retriever")

# 객체의 속성에 접근
print(my_dog.name)   # "Buddy"
print(my_dog.breed)  # "Golden Retriever"

# 객체의 메소드 호출
my_dog.bark()        # "Buddy says woof!"
