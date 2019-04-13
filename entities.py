from random import Random

class Genome:
    """ A `Genome` is a `bytearray`, often loaded from file, on which you can
        use functions likes `mutate` to affect it. Typically:

        ```python
            from entities import Genome

            e = Genome("rom_in.gb", "rom_out.gb") # load a ROM from a file
            e.mutate(.12, 1) # affect the ROM randomly (do +/-1 over 12% of it)
            e.save()         # save the newly generated ROM
            e.start()        # start the file in an associated emulator
        ```
    """
    DEBUG = __debug__ or True # overwitted for... debugging purposes ?
    LINE_SIZE = 80 # used to determine the max size of a printed line

    # START object general
    def __init__(self, file, name=None, rand=None, isData=False):
        """ Create a new `Genome` instance from file.

            If the `file` parameter is of `str`, the data are loaded from the
            file it indicate (file is open in `'rb'`). Otherwise, use `read`
            from the object.

            Data are stored in a `bytearray` object using `'ascii'` encoding.

            `name` allows you to give a name to the `Genome` this name will be
            used to `save` and `start` the file. If no name is given, it will
            take the name of the given file. This behaviour may end up
            overwriting the source file when trying to `save`.

            If the `rand` is not given, this `Genome` will generate its own.

            By default, all the data are bound to a single partition 0 of name
            "default" and of range 0 to `size` - 1.

            If `isData` is set to `True`, it toggle to a data mode where `file`
            is assumed to contains an array of data (`bytes`, `int[]`, `str`,
            or `bytearray`) that can be converted to a `bytearray`. Therefore,
            if `file` is a `str`, it use the `'ascii'` encoding.
        """
        Genome.output("Data loading..  [", end="")
        if not isData:
            if isinstance(file, str):
                file = open(file, 'rb')

            self.data = bytearray(file.read())
            self.name = name or file.name
            file.close() # USL ?
        else:
            if isinstance(file, str):
                self.data = bytearray(file, 'ascii')
            else:
                self.data = bytearray(file)
            self.name = name or file[:8]

        self.size = len(self.data)
        self.part = [("default", range(self.size))]
        self.pmap = { "default": 0 }
        Genome.output("=" * (Genome.LINE_SIZE - 19) + "=]")

        if not isinstance(rand, Random):
            rand = Random(rand)
        self.rand = rand or Random()

    def __str__(self):
        """ Return a string representation.

            Create and return a printable representation of the partition
            system for this `Genome`'s dataset.

            Note: in some certain situations (like having too many small
            partitions), some lines of the output may go beyond the
            `Genome.LINE_SIZE` character limit.
        """
        m = (Genome.LINE_SIZE - len(self) * 2 + 1) / self.size
        pushed = 0

        infos = "Name: {}, size: {:,}b\n".format(self.name, self.size)
        names = "\n"
        parts = "|"

        progress = 0

        Genome.output("Printing..      [", end="")
        for k in range(len(self)):
            n = int(len(self[k][1]) * m - 1 - pushed)
            if n < 0:
                pushed+= n

            names+= "\n{}: {} ({:,}b)".format(k, self[k][0], len(self[k][1]))
            parts+= str(k) + "-" * n + "|"

            newProgress = int(k / len(self) * (Genome.LINE_SIZE - 19))
            if progress < newProgress:
                Genome.output("=" * (newProgress - progress), end="")
                progress = newProgress
        Genome.output("=" * (Genome.LINE_SIZE - 18 - progress) + "]")

        return infos + parts + names
    # END object general

    # START partitions manipulation
    def partition(self, part):
        """ Create a partition.

            Bind a partition system to the data as described by `part`. It
            should be an array of `(str, range)` tuples.

            If the last tuple dose not implement a `range` (i.e. is only made
            of a name), it will be assigned what is left of the data.

            Note: This function does not check for overlaps nor unmapped areas.
            If two partitions have the same name, the function `Genome.idof`
            will only returns the later one. In that case, you may not use the
            name as an identifier, but rather the number.
        """
        self.part = part
        self.pmap = dict([
                (part[k] if isinstance(part[k], str) else part[k][0], k) \
                    for k in range(len(part))
            ])

        if isinstance(self[-1], str):
            r = range(self[-2][1][-1] + 1 if 1 < len(self) else 0, self.size)
            self.part[-1] = (self[-1], r)

        return self

    def __getitem__(self, k):
        """ Returns the partition `k`: a tuple (name, data_range).

            If `k` is a `str`, return the partition of name `k`.
        """
        return self.part[self.idof(k) if isinstance(k, str) else k]

    def __setitem__(self, k, v):
        """ Rename the partition `k`.

            If `k` is a `str`, rename the partition previously named `k`.

            To change a partition size, you may use `Genome.resize`.
        """
        self.part[self.idof(k) if isinstance(k, str) else k][0] = v

    def __len__(self):
        """ Return the number of partition for the data.
        """
        return len(self.part)

    def resize(self, k, before, after):
        """ Resize a partition.

            The new partition will get the last `before` bytes of the partition
            `k-1` and the first `after` bytes of the partition `k+1`. The final
            partition can not go over any edges.

            If `k` is a `str`, resize the partition of name `k`.

            Note: if another partition ends up empty (of null range), it will
            not be supressed to prevent partition number shifting.
        """
        if isinstance(k, str):
            self.resize(self.idof(k), before, after)

        r = self[k][1]
        lower = max(0, r[0] - before)
        upper = min(self.size, r[-1] + after)

        if 0 < k - 1:
            self.part[k - 1] = (self[k - 1][0], self[k - 1][1][:-before])

        if k + 1 < len(self):
            self.part[k + 1] = (self[k + 1][0], self[k + 1][1][after:])

        self.part[k] = (self[k][0], range(lower, upper))

        return self

    def get(self, k):
        """ Returns the data from the partition `k`.

            If `k` is a `str`, return the data from partition of name `k`.
        """
        if isinstance(k, str):
            k = self.idof(k)

        return self.data[self[k][1][0]:self[k][1][-1]]

    def idof(self, name):
        """ Returns the identifier of the partition by the name `name`.
        """
        return self.pmap[name]
    # END partitions manipulation

    # START data modification
    @staticmethod
    def randit(it, rand=None):
        """ Random object from iterable.

            Return an occurrence at random from the given iterable, using
            `rand` if given or else a new `Random` object.
        """
        return it[(rand or Random()).randrange(0, len(it))]

    @staticmethod
    def output(info, end="\n"):
        if Genome.DEBUG:
            print(info, end=end)

    def mutate(self, ratio, sigma, bounds=[]):
        """ Mutate the `Genome` randomly.

            Affect `ratio` of the genome's data by adding a random integer from
            `-sigma` to `+sigma`. If `sigma` is not an `int`, the random is
            done from `sigma[0]` to `sigma[-1]`.

            If `bounds` is left empty, every bytes of data may be affected. To
            restrict mutations to an area, you must precise an iterable of
            ranges (iterables) from which the destination will be chosen. If
            `bound` contains raw integers or raw string, they are interpreted
            as partition identifiers and thus replace by their partition's
            range.
        """
        if isinstance(sigma, int):
            sigma = (-sigma, +sigma)

        if not bounds:
            bounds = [range(self.size)]
        for k in range(len(bounds)):
            if isinstance(bounds[k], (int, str)):
                bounds[k] = self[bounds[k]][1]

        progress = 0
        total = int(ratio * self.size)

        Genome.output("Mutation..      [", end="")
        for k in range(total):
            p = Genome.randit(Genome.randit(bounds, self.rand), self.rand)
            new = self.data[p] + self.rand.randint(sigma[0], sigma[-1])
            self.data[p] = new % 0x100

            newProgress = int(k / total * (Genome.LINE_SIZE - 19))
            if progress < newProgress:
                Genome.output("=" * (newProgress - progress), end="")
                progress = newProgress
        Genome.output("=" * (Genome.LINE_SIZE - 18 - progress) + "]")

        return self

    def geneswap(self, amount, size, bounds=[]):
        """ Swaps random chunks of data.

            `amount` is the number of times the algorithm will be executed.

            Determines two areas of the `data`, of max size `size` (in bytes)
            and within `bounds` then swap them.

            If `bounds` is left empty, every bytes of data may be affected. To
            restrict mutations to an area, you must precise an iterable of
            ranges (iterables) from which the destination will be chosen. If
            `bound` contains raw integers or raw string, they are interpreted
            as partition identifiers and thus replace by their partition's
            range.
        """
        if not bounds:
            bounds = [range(self.size)]
        for k in range(len(bounds)):
            if isinstance(bounds[k], (int, str)):
                bounds[k] = self[bounds[k]][1]

        progress = 0

        Genome.output("Gene swapping.. [", end="")
        for k in range(amount):
            r1 = Genome.randit(bounds, self.rand)
            r2 = Genome.randit(bounds, self.rand)

            s = min((len(r1), len(r2), size))

            p1 = Genome.randit(r1[:-s])
            p2 = Genome.randit(r2[:-s])

            self.data[p1:p1+s], self.data[p2:p2+s] = self.data[p2:p2+s], \
                                                     self.data[p1:p1+s]

            newProgress = int(k / amount * (Genome.LINE_SIZE - 19))
            if progress < newProgress:
                Genome.output("=" * (newProgress - progress), end="")
                progress = newProgress
        Genome.output("=" * (Genome.LINE_SIZE - 18 - progress) + "]")

        return self
    # END data modification

    # START file management
    def save(self, file=None):
        """ Save the `Genome` into a file.

            By default (i.e. `file` not specified), saves the `Genome` in 
            file by its own name, overwriting it.

            If the `file` parameter is of `str`, the data are loaded into the
            file it indicate (file is overwritten in `'wb'`). Otherwise, use
            `write` from the object with the data (`bytearray`).
        """
        if isinstance(file, str):
            file = open(file, 'wb')

        (file or open(self.name, 'wb')).write(self.data)

        return self

    def start(self):
        """ Launch it.

            Start the `Genome`'s file using Windows' associated program. You
            may want to `save` the `Genome` beforehand as this effectively runs
            `start %name%` through the CMD.
        """
        import os
        os.startfile(self.name)

        return self
    # END file management
