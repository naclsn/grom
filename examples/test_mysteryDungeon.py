from grom import Genome, Partition

dirName = "examples\\src\\pkmn\\Pokemon Mystery Dungeon - Red Rescue Team (U)\\"
fileName = "Pokemon Mystery Dungeon - Red Rescue Team (U)" # .gba and .rps
fileSize = 0x2000000 # 33,554,432 bytes (32 Mb)

def lineParse(line):
    addresses, name = line.split(" = ", 1)
    start, end_n_size = addresses.split(" to ", 1)
    end, size = end_n_size.split(" ", 1)
    return (name.strip(), range(int(start, 16), int(end, 16) + 1))

partition = Partition(fileSize, dirName + fileName + ".rps", lineParse)
#print(partition.check()) # soooo slow...

genome = Genome(dirName + fileName + ".gba")
genome.setPartition(partition)
#genome("dump\\pokeDM.gba")

partSys = dict(
        names = [
                'Friend Area Names',
                'Type Names',
                'Formatted Type Names',
                'Abilities Names',
                'Range Names',
                'Status Names',
                'Formatted Status Names',
                'Dungeon Names',
                'IQ Skill Names',
                'Tactics Names',
                'Save Place Names',
                'Pokemon Species and Category Names'
            ] # question: rather mutate names pointer table?
    )

#genome.geneswap(150, 30, partSys['names'])("dump\\pokeDM.gba")
genome.mutate(.2, 0x80, ['Personality Test Questions'])("dump\\pokeDM.gba")
