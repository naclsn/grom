from entities import Genome

e = Genome("examples/src/kdl.gb", "test.gb")
e.partition([
        ('int', range(0x0, 0x100)),
        ('head', range(0x100, 0x150)),

        ('game')
    ])

print(e, end="\n\n")

while not input():
    #e.geneswap(10, 0x10, ['game'])
    e.mutate(.0001, 1, ['game']).save().start()
