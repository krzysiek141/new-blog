# moja_lista = ["takie", "tam", "kolejne", "słowa"]
# print(*moja_lista)

def dekorator(function):
    def wrapper():
        print("decorating works")
        return function()
    return wrapper

@dekorator
def zwykla_funkcja():
    print("To ja zwykla funkcja")
    return "Zwracam co zwracam"

# @dekorator
def test1(*args):
    print(type(args))
    print(args)
    print(*args)
    print(args[0], args[1], args[2], args[3])

def test2(**kwargs):
    print(type(kwargs))
    print(kwargs)
    print(kwargs["my_key"])
    # print("")
    # # print(**kwargs)
    # # print("")
    # print(kwargs["arg1"], kwargs["arg2"], kwargs["arg3"], kwargs["arg4"])

def dekorator(function):
    def wrapper():
        print("decorating works")
        function()
    return wrapper

#test1("siema", "ciekawe", "jak", "to", "dziala")
my_dict = {
    "my_key": "siema",
    "second_key": "witaj",
    "third_key": "cos_tam"
    }

test2(**my_dict)
# zwykla_funkcja()
# a = zwykla_funkcja()
# print(a)

# dekoratory i return