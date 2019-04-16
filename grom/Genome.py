import grom

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
    # START object general
    def __init__(self, file, name=None, rand=None, isData=False):
        """ Create a new `Genome` instance from file.

            If the `file` parameter is of `str`, the data are loaded from the
            file it indicate (file is open in `'rb'`). Otherwise, use `read`
            from the object.

            If the `rand` is not given, this `Genome` will generate its own
            (from `grom.util.random` which should be the same as default
            Python's `random`).

            Data are stored in a `bytearray` object using `'ascii'` encoding.
            For more information about data loading see `Genome.load`.
        """
        self.name = name or "noname"

        pr = grom.util.Progress("Loading data")
        self.load(file, name, isData)
        del pr

        if not isinstance(rand, grom.util.random.Random):
            rand = grom.util.random.Random(rand)
        self.rand = rand or grom.util.random.Random()

    def __str__(self):
        """ Return a string representation.

            Create and return a printable representation of the partition
            system for this `Genome`'s dataset.

            Note: in some certain situations (like having too many small
            partitions), some lines of the output may go beyond the
            `Genome.LINE_SIZE` character limit.
        """
        m = (grom.util.LINE_SIZE - len(self) * 2 + 1) / self.size
        pushed = 0

        infos = "Name: {}, size: {:,}b\n".format(self.name, self.size)
        names = "\n"
        parts = "|"

        pr = grom.util.Progress("Printing", len(self))
        for k in range(len(self)):
            n = int(len(self[k][1]) * m - 1 - pushed)
            if n < 0:
                pushed+= n

            names+= "\n{}: {} ({:,}b | from Ox{:X} to 0x{:X})".format(
                    k,
                    self[k][0],
                    len(self[k][1]),
                    self[k][1][0],
                    self[k][1][-1]
                )
            parts+= str(k) + "-" * n + "|"

            pr.update(k)
        del pr

        return infos + parts + names
    # END object general

    # START partitions manipulation
    def partition(self, part):
        """ Create a partition.

            Bind a partition system to the data as described by `part`. It
            should be an array of `(str, range)` tuples.

            If the last tuple does not implement a `range` (i.e. is only made
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

    def check(self, part=None):
        """ Check the integrity of the partition.

            For the given partition system `part` or the partition it already
            have if none is given, check for holes (unmapped part of the data)
            and overlaps (parts covered by multiple partition) as two lists of
            non-empty ranges (in this order).

            This function is quite time consuming: you should avoid using it.
            Does not check for out-of-bound partitions.

            Note that this function does not assume the partition is "sorted"
            (i.e. following ranges are not presumed to be actually next to one
            another) -- although this increases the complexity and execution
            time for very complex systems.
        """
        holes = []
        overlaps = []

        h_start, h_started = 0, False
        o_start, o_started = 0, False

        pr = grom.util.Progress("Checking", self.size)
        for k in range(self.size):
            count = len([1 for n, r in self.part if k in r])

            if not count and not h_started:
                h_start = k
                h_started = True
            elif h_start - k and count and h_started:
                holes.append(range(h_start, k))
                h_started = False

            if 1 < count and not o_started:
                o_start = k
                o_started = True
            elif o_start - k and count < 2 and o_started:
                overlaps.append(range(o_start, k))
                o_started = False

            pr.update(k)
        del pr

        return holes, overlaps

    def format(self, newPart): # I guess it could be in "data manipulation"...
        """ Reformat the `Genome`.

            Reformatting the `Genome` only swaps the partitions around
            according to the `newPart` parameter: it must be a list of valid
            partition identifiers (either `str` or `int`). The new data will
            contain the old data from the matching partition.

            Note: for this function to operate, `Genome.check` must return
            two empty list. Does not raise exception otherwise, but returns
            None.
        """
        if any(self.check()):
            return None # USL

        part = []
        data = bytearray([0] * self.size)

        av = 0
        for p in newPart:
            n, r = self[p]

            part.append((n, range(av, av + len(r))))
            data[part[-1][1][0]:part[-1][1][-1]] = self.data[r[0]:r[-1]]

            av+= len(r)

        self.part = part
        self.data = data

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
    def mutate(self, ratio, sigma, bounds=[]):
        """ Mutate the `Genome` randomly.

            Affect `ratio` of the genome's data by adding a random integer from
            `-sigma` to `+sigma`. If `sigma` is not an `int`, the random is
            done from `sigma[0]` to `sigma[-1]`. The value may overflow or
            underflow but it will not affect any surrounding data.

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
        else:
            for k in range(len(bounds)):
                if isinstance(bounds[k], (int, str)):
                    bounds[k] = self[bounds[k]][1]

        randit = grom.util.randit
        total = int(ratio * self.size)

        pr = grom.util.Progress("Mutation", total)
        for k in range(total):
            p = randit(randit(bounds, self.rand), self.rand)
            new = self.data[p] + self.rand.randint(sigma[0], sigma[-1])
            self.data[p] = new % 0x100

            pr.update(k)
        del pr

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
        else:
            for k in range(len(bounds)):
                if isinstance(bounds[k], (int, str)):
                    bounds[k] = self[bounds[k]][1]

        pr = grom.util.Progress("Gene swapping", amount)
        for k in range(amount):
            r1 = grom.util.randit(bounds, self.rand)
            r2 = grom.util.randit(bounds, self.rand)

            s = min((len(r1), len(r2), size))

            p1 = grom.util.randit(r1[:-s])
            p2 = grom.util.randit(r2[:-s])

            self.data[p1:p1+s], self.data[p2:p2+s] = self.data[p2:p2+s], \
                                                     self.data[p1:p1+s]

            pr.update(k)
        del pr

        return self

    def crossover(self, mate, name=None, rand=None, bounds=[], crosser=None):
        """ Create a crossover `Genome` from parents.

            `self` and `mate` are crossed over into a new `Genome`. This
            algorithm is not yet finished, and only for testing and
            placeholding purposes. `amount` is the number of times the
            algorithm will be executed.

            For each given bound, determines (randomly) which chunk of data
            (from eight parent) will go into the new `Genome`. The `bounds`
            parameters should be a full and flawless (no holes, no overlaps)
            partition for the data. Both parent should have the same size.
            Note that none of this is checked here as of right now.

            If the `crosser` function is not `None`, it is called with for
            parameters the two chunks of data to swap as `bytearray`s (`self`
            first, then `mate`), and expected an output of data the same size,
            formatted as on of: `int[]` `bytes` `str` (supposedly 'ascii'
            encoded) or `bytearray`. The new `Genome`'s data is initialized at
            `'b0x00'`, therefore if `crosser` does not return an appropriated
            result, the part will be kept at zeros.

            If not name is given, the name will be "`self.name`x`mate.name`".

            If the `rand` is not given, the new `Genome` will generate its own.

            If `bounds` is left empty, it will be loaded from the partition
            system of this `Genome` (`self`). To restrict mutations to an area,
            you must precise an iterable of ranges (iterables) from which the
            destination will be chosen. If `bound` contains raw integers or raw
            string, they are interpreted as partition identifiers and thus
            replace by their partition's range. Note that `mate`'s partition is
            never taken into account.

            Lastly, only `self`'s random is used.
        """
        if not bounds:
            bounds = [r for n, r in self.part]
        else:
            for k in range(len(bounds)):
                if isinstance(bounds[k], (int, str)):
                    bounds[k] = self[bounds[k]][1]

        data = bytearray([0] * self.size)

        pr = grom.util.Progress("Crossing over", len(bounds))
        for k in range(len(bounds)):
            st, ed = bounds[k][0], bounds[k][-1]

            if callable(crosser):
                r = crosser(self.data[st:ed], mate.data[st:ed])

                if isinstance(r, str):
                    r = bytearray(r, 'ascii')
                if isinstance(r, (bytes, list, tuple)):
                    r = bytearray(r)
            else:
                r = grom.util.randit((self.data, mate.data), self.rand)[st:ed]

            data[st:ed] = r

            pr.update(k)
        del pr

        return Genome(data, name or self.name + "x" + mate.name, rand, True)
    # END data modification

    # START file management
    def load(self, file=None, name=None, isData=False):
        """ Load the `Genome` from a file.

            `name` allows you to give a name to the `Genome` this name will be
            used to `save` and `start` the file. If no name is given, it will
            take the name of the given file. This behaviour may end up
            overwriting the source file when trying to `save`. If the `isData`
            if `True` and no name is given, the `Genome` will take for name the
            first 8 (or less if not enough) bytes of raw data.

            By default, all the data are bound to a single partition 0 of name
            "default" and of range 0 to `size` - 1.

            If `isData` is set to `True`, it toggle to a data mode where `file`
            is assumed to contains an array of data (`bytes`, `int[]`, `str`,
            or `bytearray`) that can be converted to a `bytearray`. Therefore,
            if `file` is a `str`, it use the `'ascii'` encoding.

            Finally, if `file` if `None`, try to load `self.name` as a file.
        """
        if name:
            self.name = name

        if not file:
            file = self.name
            isData = False

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
        """ 'Launch' the `Genome`.

            Start the `Genome`'s file with OS' associated program (using
            Python's `os.startfile`). You may want to `save` the `Genome`
            beforehand. Uses `grom.util.os`.
        """
        grom.util.os.startfile(self.name)

        return self

    def __call__(self, file=None):
        """ Save then start.

            See both `Genome.save` and `Genome.start` functions' documentation
            for more detailed information.

            If a `file` is given, save into this file. The `name` of the
            `Genome` is not modified.
        """
        return self.save(file).start()
    # END file management