from grom import Genome, util

g = Genome("examples/src/img1.bmp", "output.bmp")

g.partition([
    ('head', range(0, 0x36)),
    ('a', range(0x36, 0x1A132)),
    ('b', range(0x1A132, 0x1AFF0)),
    ('c', range(0x1AFF1, 0xA1F1F)),
    ('d')
])
print(g)
print(g.check())

g.mutate(.5, 0x7F, ['a', 'b', 'c'])()
