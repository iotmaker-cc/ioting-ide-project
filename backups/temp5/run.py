# run.py

class Run:
    def __init__(self):
        
        self.functions = []
        
    def add(self,function):
        self.functions.append(function)
        
    def remove(self,function):
        
        try:
            self.functions.remove(function)
        except ValueError:
            pass
        
    def run(self):
        
        for f in self.functions:
            f()
            