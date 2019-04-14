""" An example to illustrate the actions of the crossover function.

    In this example, we partition two 640 by 480 BMP files by line, before
    calling the crossover algorithm with an alternating function, and with the
    default random function.
"""

from grom import Genome
Genome.DEBUG = False

# create a line-by-line partition system for a `.bmp` file of 640x480,
# keeping the signature separated
lineSize = 640 * 3
P = [('head', range(0, 0x36))] + \
    [('l' + str(k), range(0x36 + lineSize * k, 0x36 + lineSize * (k+1))) \
     for k in range(480)]

# this function will return `d1` every even calls and `d2` every odd calls
counter = 0
def f(d1, d2):
    global counter
    counter+= 1
    return (d1, d2)[counter % 2]

# create `Genome` from the images and apply partition system
a = Genome("examples/src/img1.bmp").partition(P)
b = Genome("examples/src/img2.bmp").partition(P)

# crossover the images then ask OS to open the resulting "test1.bmp"
a.crossover(b, "test1.bmp", crosser=f)()

# crossover with the default random function, along the lines of the image
a.crossover(b, "test2.bmp")()
