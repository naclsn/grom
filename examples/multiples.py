from grom import Genome, util
util.DEBUG = False

# file size: 0x20 (32 char, raw text)
# mapping along words in first file (a.txt)
P = [
        ('ceci',       range(0x00, 0x05)),
        ('est',        range(0x05, 0x09)),
        ('un',         range(0x09, 0x0C)),
        ('txt',        range(0x0C, 0x10)),
        ('de',         range(0x10, 0x13)),
        ('32',         range(0x13, 0x16)),
        ('caracteres', range(0x16, 0x20))
    ]

a = Genome("examples\\src\\a.txt").partition(P)
b = Genome("examples\\src\\b.txt").partition(P)

a(file="dump\\output0.txt")
a.crossover(b)("dump\\output1.txt")
a.format(['32', 'caracteres', 'est', 'ceci', 'de', 'un', 'txt'])("dump\\output2.txt")
a.mutate(.5, 5, ['ceci', 'caracteres'])("dump\\output3.txt")
