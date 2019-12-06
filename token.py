from enum import Enum


class TokenType(Enum):
    ID = 1
    STR = 2
    NU = 3
    ST = 4
    KW = 6


class Token:
    def __init__(self, ty, val):
        self.type = ty
        self.value = val

    def getValue(self):
        return self.value + " " + str(self.type)

    def getType(self):
        return self.type
