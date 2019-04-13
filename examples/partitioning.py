""" An example to demonstrate the use of partitions.

    (Working, but not up-to-date, as in not using latest functionalities.)
"""

from grom import Genome
Genome.DEBUG = False

e = Genome("examples/src/kdl.gb", "examples/test.gb")
print(e, end="\n\n\n")

e.partition([
        ("hello", range(0X0, 0x6543)),
        ("world", range(0x6543, 0x12345)),
        ("!", range(0x12345, e.size))
    ])
print(e, end="\n\n\n")

e.partition([
        ("int", range(0x0, 0x100)),
        ("head", range(0x100, 0x150)),

        ("game", range(0x150, e.size))
    ])
print(e, end="\n\n\n")

p = e.idof("game") # retrieve partition "2: game"
e.mutate(.12, 1, [p]) # only mutate the 'game' partition
e.save().start()
