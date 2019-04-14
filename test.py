from grom import Genome

g = Genome("examples/src/img1.bmp", "output.bmp")

# apply de discussed partition system
g.partition([
    ('head', range(0, 0x36)),
    ('raw') # if no range is provided, the range will cover up to EOF
])
print(g)

g.mutate(.05, 0x7F, ['raw']) # only affect the 'raw' partition
g()
