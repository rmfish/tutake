from test.extends import say_hello_ext


class A:

    def __init__(self):
        self.name = "JJ"

    def say_hello(self):
        print("Hi my name is {}".format(self.name))


setattr(A, 'say_hello', say_hello_ext)

if __name__ == '__main__':
    a = A()
    a.say_hello()
