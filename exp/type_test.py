"""Module created for testing types.MethodType()"""

import types

class Class1():
    def __init__(self):
        self.name = "Class1"

def func1(self):
    print("Passed in function result: {}".format(self.name))
    
inst1 = Class1()

print("Inst1 attribute: {}".format(inst1.name))
    
inst1.printName = types.MethodType(func1, inst1)
 
inst1.printName()

print("=============================")
print(types.MethodType.__doc__)
print("=============================")
print(types.__dict__)


