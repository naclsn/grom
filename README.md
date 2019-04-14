# **grom**

## Overview

**grom** defines a `Genome` class meant to be loaded from a file as an array of
bytes. You can then apply modification function like `mutate` or `crossover` to
edit the `Genome` or generate a new `Genome`. Finally you can use `save` to
save into a file, then `start` to run the file with the associated program.

The same algorithms will works regardless of the data itself: the file you use
may vary from `.gb` to plain `.exe` or even sources files like `.png`...

---

## The `Genome`

The `Genome` is an object built around a `bytearray` to ease its loading,
saving and modification:

```python
from grom import Genome

# load the content of "test/file_name.ext" into a `bytearray`
g = Genome("test/file_name.ext", "genome/output_name.ext")
```

To a loaded `Genome`, you can apply the following
data modification function:

```python
g.mutate(.001, 1) # apply a random mutation of ampliture 1 to .1% of the data

g.geneswap(10, 8) # swap 10 random chunks of 8 bytes in the data
```

The crossover function works a bit differently as it does not modify the
`Genome` itself, but rather create a new one:
```python
g2 = Genom("another/file_name.ext")

# crossover `g` and `g2` into a new `Genome`
child = g.crossover(g2, "child/file_name.ext")
```

You may then save the `Genome` to use with its associated program:
```python
child.save() # save the child into "child/file_name.ext"
child.start() # start the file using python's `os.startfile`

# or simply:
child()
```

> Note that almost every function (all function that does not return something)
> return `self` to allow for chaining:
> ```python
> Genome(filename).partition(parts).mutate(tx, amp).save().start()
> ```

---

## Partitioning

You can define a partition system to facilitate gene modification, like local
mutations. For that, the `Genome` object will behave like an array of delimited
and named spaces, attributed to a range in the data.

Let's take classic `.bmp` file:
1. The first 0x36 bytes are reserved for signature and header information
0. Bytes from 0x36 to EOF contains the raw pixel data we want to modify

You may then want to define a matching partition: this will enable you to
control which data will be affected by `mutate`, and keep the file signature
sound.

```python
g = Genome("some/image.bmp", "output.bmp")

# apply de discussed partition system
g.partition([
    ('head', range(0, 0x36)),
    ('raw') # if no range is provided for the last one, it will cover up to EOF
])

g.mutate(.50, 0x7F, ['raw']) # only affect the 'raw' partition
```

You can also, if you have two similar file (in size and signature) set up
arbitrary partition for the data before using `crossover`: the result will be a
mashup of both file along the given partition (say e.g. partitioning line by
line, with `crosser` function returning odds of `self` and evens of `mate`).
