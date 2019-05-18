import grom

dirName = "examples\\src\\pkmn\\Pokemon Mystery Dungeon - Red Rescue Team (U)\\"
fileName = "Pokemon Mystery Dungeon - Red Rescue Team (U).gba"
resultName = "C:\\Users\\sincs\\OneDrive\\Bureau\\dump\\test.gba"

g = grom.Genome(dirName + fileName)

ratio = .02
size = 0x10
count = int(ratio * g.size / size)
part = [range(0x100, g.size)]

# g.mutate(.00002, 1, part)
g.geneswap(count, size, part)

g(resultName, pause=False)
