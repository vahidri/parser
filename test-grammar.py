import engine as libg

fileGrammar = 'g.txt'
g = libg.reader(fileGrammar)
libg.gprint(g)
print()
for n in range(len(g)):
    print('PREDICT of', n, 'is', libg.predict(g, n))
print("\nParse Table:")
libg.ppt(libg.makePT(g))

print('\nLL(1) check: ', end='')
if libg.isLL1(g):
    print('Yes')
else:
    print('No')
    libg.faults(g)
