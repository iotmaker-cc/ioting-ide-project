class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        pass  # 자식 클래스에서 구현

class Dog(Animal):
    def speak(self):
        print(f"{self.name} says woof!")

class Cat(Animal):
    def speak(self):
        print(f"{self.name} says meow!")

my_dog = Dog("Buddy")
my_cat = Cat("Whiskers")

my_dog.speak()  # "Buddy says woof!"
my_cat.speak()  # "Whiskers says meow!"
