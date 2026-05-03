class Parent:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        print(f"Hello, my name is {self.name}")

class Child(Parent):
    def __init__(self, name, age):
        # 부모 클래스의 __init__ 메소드를 호출하여 name을 초기화
        super().__init__(name)
        self.age = age
    
    def greet(self):
        # 부모 클래스의 greet 메소드를 호출
        super().greet()
        print(f"I am {self.age} years old")

# 객체 생성 및 메소드 호출
child = Child("Alice", 12)
child.greet()