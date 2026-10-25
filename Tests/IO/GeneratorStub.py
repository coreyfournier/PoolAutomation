from IO.GeneratorRepo import GeneratorRepo

class GeneratorStub(GeneratorRepo):
    def __init__(self, on:bool) -> None:
        self.on = on
        #How many times it was asked, to check the polling interval
        self.checks = 0

    def isOn(self):
        self.checks += 1
        return self.on
