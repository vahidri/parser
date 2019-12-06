from scanner import *

sc = scanner("code.c")

tkn = sc.nextToken().getValue()
while tkn != "$":
    print(tkn)
    try:
        tkn = sc.nextToken().getValue()
    except:
        print("done")
        break
