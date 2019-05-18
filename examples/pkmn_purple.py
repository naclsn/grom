from grom import Genome, Generation
from grom.util import randit
from random import Random

def parse(line): # lines are formatted: "$value $name" w/ value in hex
    value, name = line.split(" ", 1)
    return name, [int(value, 16)]

P = Generation.partitionFromFile("examples\\src\\pkmn\\rom_map.rps", parse)

a = Genome("examples\\src\\pkmn\\pkmn_red.gb").partition(P)
b = Genome("examples\\src\\pkmn\\pkmn_blue.gb").partition(P)

def crx(a, b, k):
    r = Random()
    return [randit((a[k], b[k]), r) for k in range(len(a))]

Genome.crossover(a, b, crosser=crx)("dump\\pkmn_purple.gb")
