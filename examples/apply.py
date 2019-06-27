import random
import grom
grom.debug(False)

dirName = "dump\\"
inputName = "example.bmp"
outputName = "output.bmp"

g = grom.Genome(dirName + inputName, partition=[
    ('head', 0x76),
    ('raw')
])

print(g)
print(g.partition)

g.apply(lambda x: 255 - x, ['raw'])
g(dirName + outputName, pause=False)
