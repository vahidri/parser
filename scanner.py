import re
from token import Token, TokenType


class scanner:
    def __init__(self, filePath):
        self.fileCode = open(filePath, "r")
        self.fileContent = self.fileCode.read()
        self.fileCode.close()
        self.fileSt = open("special_tokens.txt")
        self.specialTokens = self.fileSt.read().split()
        self.fileSt.close()
        self.fileKw = open("keywords.txt")
        self.keywords = self.fileKw.read().split()
        self.fileKw.close()

        self.curCh = -1
        self.ch = ''
        self.size = len(self.fileContent)
        self.fileContent += " $"

    def printToken(self):
        print(self.fileContent[0])

    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass
        return False

    def nextChar(self):
        if self.curCh < self.size:
            self.curCh += 1
            self.ch = self.fileContent[self.curCh]
            return True
        else:
            return False

    def nextToken(self):
        value = ""
        while self.nextChar():
            value += self.fileContent[self.curCh]
            if value in self.specialTokens:
                self.nextChar()
                while value + self.ch in self.specialTokens:
                    value += self.ch
                    self.nextChar()
                self.curCh -= 1
                return Token(TokenType.ST, value)
            elif value is '"':
                self.nextChar()
                value += self.fileContent[self.curCh]
                while value[-1] != '"':
                    self.nextChar()
                    value += self.fileContent[self.curCh]
                if len(value) > 1:
                    return Token(TokenType.STR, value)
            elif self.isNumber(value):
                while self.isNumber(self.fileContent[self.curCh + 1]):
                    value += self.fileContent[self.curCh + 1]
                    self.nextChar()
                return Token(TokenType.NU, value.strip())
            elif "$" == value.strip():
                return Token(TokenType.DLR, value.strip())
            elif value[-1] in self.specialTokens:
                self.curCh -= 1
                value = value[:-1]
                return Token(TokenType.ID, value.strip())
            elif "" == value.strip():
                value = ""
            elif " " == value[-1]:
                if value.strip() == "":
                    value = ""
                else:
                    return Token(TokenType.ID, value.strip())
            elif value.strip() in self.keywords:
                return Token(TokenType.KW, value.strip())
