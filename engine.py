"""
grammar engine for Top Down LL(1) syntax checker, for C-like language
by Vahid Ramazani
@vramazani
"""

import re
from pprint import pprint as ppt


def dbg(*inp, sep=' ', end='\n'):
    return
    print('DBG>> ', end='')
    print(*inp, sep=sep, end=end)


err = print

stackFollow = []

##Memoization
cacheFirst = {}
cacheFollow = {}
cachePedict = {}
cacheNullable = set()
cacheNullableNot = set()
cacheHead = []

##constants
reVar = re.compile('[A-Z]+[0-9]*')  ##RegEx for VARiables
nil = 'nil'
dollar = '$'  ##indicates end of token stream


def gprint(gram):
    for i, p in enumerate(gram):
        print(i, p[0], '->', p[1:])


def override(gram, h, t, n):
    gram[(h, t)] = n


def reader(pathInp):  ##reads the grammar
    ##reset the caches
    global cacheFirst, cacheFollow, cachePedict, cacheNullable, cacheNullableNot, cacheHead
    cacheFirst = {}
    cacheFollow = {}
    cachePedict = {}
    cacheNullable = set()
    cacheNullableNot = set()
    cacheHead = []

    G = []
    i = 0
    with open(pathInp, mode='r') as f:
        for line in f:
            i += 1
            p = []
            for s in line.split():
                p.append(s.rstrip('\n'))
            if p[1] == '->':
                del p[1]
                if p[0] not in cacheHead:
                    cacheHead.append(p[0])
                G.append(p)
            else:
                err('ERR(wrong production): ', line)
    return G


def getParts(gram):  ##get partitions of grammar
    outy = {h: [] for h in cacheHead}
    for i, prod in enumerate(gram):
        outy[prod[0]].append(i)
    return outy


def getTerms(gram):
    s = set()
    for p in gram:
        for seg in p[1:]:
            if isTerm(seg):
                s.add(seg)
    return sorted(list(s))


def makeRHST(gram):
    rhst = []
    for p in gram:
        rhst.append(list(reversed(p[1:])))
    return rhst


def makePT(gram):  ##ParseTable, a dict of (heads, terms) -> prod nu
    ##list[var][token]
    preds = [predict(gram, n) for n in range(len(gram))]
    terms = getTerms(gram)
    terms.append(dollar)

    #table = { (h, t): pterr for h in cacheHead for t in terms}
    table = {}
    for nu, s in enumerate(preds):
        for t in s:
            if (gram[nu][0], t) in table:
                if "__main__" == __name__:
                    print('overwrite!', (gram[nu][0], t), ':',
                          table[(gram[nu][0], t)], 'with', nu)
            table[(gram[nu][0], t)] = nu
    return table


def isNil(seg):
    if seg == nil:
        return True
    return False


def isVar(seg):
    if seg in cacheHead:
        return True
    return False


def isValidVar(seg):
    if isNil(seg):
        return False
    if seg == dollar:
        return False
    m = reVar.match(seg)
    if m is not None:
        assert m.group() == seg, ('ERR(wrong segment in production): ', seg)
        return True
        #return m.group() == seg ##added assert instead
    return False


def isTerm(seg):
    if isNil(seg):
        return False
    if seg == dollar:
        return False
    if seg in cacheHead:
        return False
    return not seg[0].isupper()


def isNullable(gram, head):  ##is a Variable(head) of grammar, Nullable or not
    if head in cacheNullable:
        return True
    if head in cacheNullableNot:
        return False
    parts = getParts(gram)
    prods = parts[head]  ##a list of numbers
    last = False  ##last check was nullable
    for n in prods:  ##production numbers of given var 'head'
        last = False
        body = gram[n][1:]
        if isNil(body[0]):
            assert len(body) == 1, ('ERR(more than nil in body:', body)
            cacheNullable.add(head)
            return True
        for seg in body:
            if isTerm(seg):
                last = False
                break
            else:  ##'seg' is a Var
                if isNullable(gram, seg):
                    last = True  ##no break; check the remaining
                else:
                    last = False
                    break
        if last:  ##this production is nullable
            cacheNullable.add(head)
            return True
    cacheNullableNot.add(head)
    return False


def isNullable_list(gram, inpList):
    if inpList == [nil]:
        return True
    for i, seg in enumerate(inpList):
        assert seg != nil
        if isTerm(seg):
            return False, i
        ##else, seg is a var
        if not isNullable(gram, seg):
            return False, i
    return True


def first(gram, head):
    if head in cacheFirst:
        return cacheFirst[head]
    outy = set()
    parts = getParts(gram)
    prods = parts[head]  ##a list of numbers
    for n in prods:  ##production numbers of given var 'head'
        body = gram[n][1:]
        if isNil(body[0]):
            continue
        for seg in body:
            if isTerm(seg):
                outy.add(seg)
                break
            else:  ##'seg' is a Var
                outy.update(first(gram, seg))
                if not isNullable(gram, seg):
                    break
    cacheFirst[head] = outy
    return outy


def first_list(gram, inpList):
    outy = set()
    if inpList == [nil]:
        #err('WARN(wrong usage)')
        return []
    for seg in inpList:
        if isTerm(seg):
            outy.add(seg)
            break
        ##it's a var
        outy.update(first(gram, seg))
        if not isNullable(gram, seg):
            break
    return outy


def find(gram, nu, seg):  ##find 'seg' in body of production 'nu' of 'gram'
    outy = []
    for i, s in enumerate(gram[nu][1:]):
        if seg == s:
            outy.append(i)
    return outy


def findall(gram, seg):  ##find 'seg' in body of all productions
    outy = []
    for i in range(len(gram)):
        outy.append(find(gram, i, seg))
    return outy


def follow(gram, head):
    if head in cacheFollow:
        return cacheFollow[head]

    if head in stackFollow:
        dbg('stackFollow repeated (',
            stackFollow.index(head),
            '/',
            len(stackFollow),
            ') \'',
            head,
            '\'',
            sep='')
        return None
    else:
        dbg('stackFollow PUSH', head)
        stackFollow.append(head)
    outy = set()
    fa = findall(gram, head)
    if all(not l for l in fa):
        pass  ##('no instance found')
    else:
        for n, l in enumerate(fa):
            for loc in l:
                dbg(head, 'in', gram[n][0])
                if len(
                        gram[n]
                ) == loc + 2:  ##it is the last segment in the production
                    if head != gram[n][0]:  ##not necessary(cuz stackFollow), just to optimize
                        f = follow(gram, gram[n][0])
                        if f is not None:
                            outy.update(follow(gram, gram[n][0]))
                else:
                    outy.update(first_list(gram, gram[n][
                        loc + 2:]))  ##+1 for the head, +1 for the var itself
                    if True == isNullable_list(gram, gram[n][loc + 2:]):
                        dbg("next is nullable")
                        if head != gram[n][0]:  ##not necessary(cuz stackFollow), just to optimize
                            f = follow(gram, gram[n][0])
                            if f is not None:
                                outy.update(follow(gram, gram[n][0]))
    if gram[0][0] == head:
        outy.add(dollar)
    #stackFollow.remove(head)
    if stackFollow[-1] != head:
        print("WHAT?!")
    else:
        dbg('stackFollow pop', head)
        stackFollow.pop()
    cacheFollow[head] = outy
    return outy


def predict(gram, nu):  ##production NUmber in grammar list
    if nu in cachePedict:
        return cachePedict[nu]
    outy = set()
    outy.update(first_list(gram, gram[nu][1:]))
    if True == isNullable_list(gram, gram[nu][1:]):
        outy.update(follow(gram, gram[nu][0]))
    cachePedict[nu] = outy
    return outy


def areDisjoint(l):  ##'l' is a list of sets
    for i, A in enumerate(l):
        for j, B in enumerate(l):
            if j > i:
                if not A.isdisjoint(B):
                    return False
    return True


def faults(gram):
    parts = getParts(gram)
    outy = []
    for head in cacheHead:
        prods = parts[head]
        if 1 == len(prods):
            continue
        ##else
        pre = [predict(gram, n) for n in prods]
        for i, A in enumerate(pre):
            for j, B in enumerate(pre):
                if j > i:
                    if not A.isdisjoint(B):
                        x = prods[i]
                        y = prods[j]
                        outy.append(set([x, y]))
                        print(x + 1, gram[x][0], ':', pre[i])
                        print(y + 1, gram[y][0], ':', pre[j])
                        print('intersection:', A & B)
    return outy


def isLL1(gram):
    parts = getParts(gram)
    for head in cacheHead:
        prods = parts[head]
        if 1 == len(prods):
            continue
        ##else
        #if len(set([gram[x][0] for x in prods])) != 1:
        #    print("WRONG")
        #    print(prods)
        #    quit()
        pre = [predict(gram, n) for n in prods]
        if not areDisjoint(pre):
            return False
    return True


def start(g):
    return g[0][0]


if "__main__" == __name__:  ###TESTS
    pathGrammar = 'g.txt'
    g = reader(pathGrammar)
    for h in cacheHead:
        first(g, h)
    #ppt(cacheFirst)
    for h in cacheHead:
        follow(g, h)
    #ppt(cacheFollow)
    #quit()
    ll1chk = isLL1(g)
    print('LL(1) check:', ll1chk)
    if not ll1chk:
        print('Faults:')
        ppt(faults(g))
        print()
    ppt(makePT(g))
    quit()
    #gprint(g)
    print('\nRHST:')
    ppt(makeRHST(g))
    print('\nPT:')
    ppt(makePT(g))
    quit()
    for h in cacheHead:
        print('First of', h, 'is', first(g, h))
    for h in cacheHead:
        print('Follow of', h, 'is', follow(g, h))
    for n in range(len(g)):
        print('PREDICT of', n, 'is', predict(g, n))
    quit()
