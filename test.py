from grom import *

dirName = "examples\\src\\pkmn\\"
fileSize = 0x2000000 # 33,554,432 bytes (32 Mb)

names = [
        'Move Names',
        'Item Names'
    ]
pictures = [
        'Pokemon Picture Data (Set 1)',
        'Pokemon Picture Data (Set 2)',
        'Pokemon Picture Data (Set 3)',
        'Pokemon Picture Data (Set 4)',
        'Pokemon Picture Data (Set 5)'
    ]
data = [
        'Moves Data',
        'Pokemon Evolutions & Learned Moves'
        #'General Pokemon Data',
        #'Bank in which Pokemon Base Stats are stored'
    ]
pointers = [
        'Pokedex Pointers',
        'Kinds of Pokemon Text, Height, Weight, Pokedex Pointers',
        'Evolution/Attacks Learned Pointers'
    ]
locations = {
        'Header': [],
        'Objects': [],
        'Data': [],
        'Script': [],
        'Pointers': []
    }

def lineParse(lineCurr, lineNext):
    address, name = lineCurr.split(' ', 1)
    name.strip()

    if '-' in address:
        st, ed = address.split('-')

        if not ed:
            ed = int(lineNext.split(' ')[0].split('-')[0].strip('$'), 16) - 1
        else:
            ed = int(ed, 16)
        st = int(st, 16)

    elif address[0] == '$':
        st = int(address.strip('$-'), 16)
        ed = int(lineNext.split(' ')[0].split('-')[0].strip('$'), 16) - 1

        locations[name.strip('"').split(' ')[-1]].append(name)

    return (name, range(st, ed + 1))

P = Partition(fileSize, dirName + "rom_map.rps", lineParse)
G = Generation(P)

g = Genome(dirName + "pkmn_red.gb")
G.append(g)

# g.geneswap(128, 8, names)
# g.geneswap(512, 128, pictures)
# g.mutate(1, 0x80, data)
# g.mutate(1, 0x80, data)
# g.mutate(.02, 1, pointers)
g.geneswap(222, 1, locations['Data'].copy())

g("C:\\Users\\sincs\\OneDrive\\Bureau\\dump\\test.gb", pause=False)
