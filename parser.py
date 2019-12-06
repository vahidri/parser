"""
Top Down LL(1) Parser, for a C-like language
by Vahid Ramazani
@vramazani
"""

from scanner import scanner
from token import Token, TokenType
from engine import reader, makePT, makeRHST, start, dollar, nil, isVar, isTerm

##globals
pathCode = 'code.c'
pathGram = 'g.txt'
scn = scanner(pathCode)
gram = reader(pathGram)
pt = makePT(gram)
rhst = makeRHST(gram)
codepassed = []

##parse stack
ps = []
push = ps.append
pop = ps.pop


def top():
    global ps
    return ps[-1]


def dbg(*inp):  ##bring the 'print' before return to see DBG in stdout
    return
    print('DBG>>', *inp)


def error(inp=None):
    print("ERR", inp)
    print('Code Passed:')
    print(codepassed)
    eChar = 0
    eCountLine = 0
    eLinePrev = ''
    eLine = ''
    with open(pathCode) as f:
        for i, l in enumerate(f):
            eChar += len(l)
            if eChar > scn.curCh:
                eChar -= len(l)
                eCountLine = i
                eLine = l
                break
            eLinePrev = l
    print('ERROR in Line', eCountLine, ', Char', scn.curCh - eChar, ':')
    print(eCountLine - 1, [eLinePrev])
    print(eCountLine, [eLine])
    print(eCountLine, [' ' * (scn.curCh - eChar - 1) + '^'])


def tkn2str(t):
    if '$' == t:
        return '$'
    elif None == t:
        dbg('NONE')
        return '$'
    elif t.type == TokenType.ID:
        return 'id'
    elif t.type == TokenType.NU:
        return 'nu'
    elif t.type == TokenType.ST or t.type == TokenType.KW:
        return t.value
    else:
        print("ERR UNDEFINED")


def accept():
    print("SUCCESS")
    quit()


if "__main__" == __name__:
    push(dollar)
    push(start(gram))
    tkn = scn.nextToken()
    tknStr = tkn2str(tkn)
    codepassed.append(tknStr)
    while True:
        dbg('top:', [top()], '| tkn:', [tknStr])
        dbg('PS:', ps)

        if isTerm(top()):
            dbg('isTerm:', [top()])
            if (top() == tknStr):
                dbg('matched:', [top()], [tkn.value])
                pop()
                #dbg('pop')
                tkn = scn.nextToken()
                tknStr = tkn2str(tkn)
                codepassed.append(tknStr)
                dbg('next')
            else:
                error(('can not match top with term:', [top()], [tknStr]))
                break
        elif isVar(top()):
            dbg('isVar:', [top()])
            #print(tkn.TokenType, tkn.value)
            if (top(), tknStr) not in pt:
                error([(top(), tknStr), 'not in ParseTable'])
                break
            prod = pt[(top(), tknStr)]
            pop()
            dbg('rhst:', rhst[prod])
            for seg in rhst[prod]:
                push(seg)
        elif top() == nil:
            pop()
        elif top() == dollar:
            dbg(dollar)
            if '$' == tknStr:
                accept()
            else:
                error(dollar)
            break
