import grom

class Genome:
    """ A `Genome` is a `bytearray`, often loaded from file, on which you can
        use functions likes `mutate` to affect it.

        `partition` designate a full `grom.Partition` system or a list of
        `tuples(str, int)`.
        `part` is always a list of partition identifiers (either `str` names or
        `int` ID).
    """
    # START object general
    def __init__(self, file, isData=False, name=None, rand=None, partition=[]):
        # TODO: list members
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

        self.setPartition(partition)

    def copy(self, name=None):
        return Genome(self.data, isData=True, name=name or self.name + "_copy")

    def setPartition(self, partition):
        if isinstance(partition, grom.Partition):
            self.partition = partition
        else:
            self.partition = grom.Partition(self.size, partition)

        return self

    def __str__(self):
        return "Genome {} (size: {:,}b)".format(self.name, self.size)
    # END object general

    # START file management
    def load(self, file=None, isData=False, name=None):
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
            file.close() # USL?
        else:
            if isinstance(file, str):
                self.data = bytearray(file, 'ascii')
            else:
                self.data = bytearray(file)

        self.size = len(self.data)
        self.partition = grom.Partition(self.size)

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

    def start(self, file=None, com=None, pause=True):
        """ 'Launch' the `Genome`.

            Start the `Genome`'s file with OS' associated program (using
            Python's `os.startfile`). You may want to `save` the `Genome`
            beforehand. Uses `grom.util.os`.

            Starts `file` instead if given, the name is not modified.

            If `com` is not `None`, runs "$com $file" in a subshell through
            `os.system`.

            `pause` specifies weather the program should be halted for the
            execution of the generated file.
        """
        if com:
            grom.util.os.system(com + " " + (file or self.name))
        else:
            grom.util.os.startfile(file or self.name)

        if pause:
            input("Press Enter to continue... ")

        return self

    def __call__(self, file=None, com=None, pause=True):
        """ Save then start.

            See both `Genome.save` and `Genome.start` functions' documentation
            for more detailed information.

            If a `file` is given, save into this file. The `name` of the
            `Genome` is not modified.

            If `com` is not `None`, runs "$com $file" in a subshell through
            `os.system`.

            `pause` specifies weather the program should be halted for the
            execution of the generated file.
        """
        return self.save(file).start(file, com, pause)
    # END file management

    # START data modification
    def __getitem__(self, k):
        """ Gets the data at `k`.

            If `k` is `str` or `int`, gets the range from partition `k`.
            Otherwise, `k` should be a `slice` or an `int` in `range(size)`.
        """
        if isinstance(k, (int, str)):
            r = self.partition[k]
            k = slice(r[0], r[-1] + 1)

        return self.data[k]

    def __setitem__(self, k, v):
        """ Sets the data at `k`.

            If `k` is `str` or `int`, gets the range from partition `k`.
            Otherwise, `k` should be a `slice` or an `int` in `range(size)`.
        """
        if isinstance(k, (int, str)):
            r = self.partition[k]
            k = slice(r[0], r[-1] + 1)

        self.data[k] = v

    def __len__(self):
        """ Returns the size of the data (in bytes).
        """
        return self.size

    def mutate(self, ratio, sigma, part=[]):
        """ Mutate the `Genome` randomly.

            Affect `ratio` of the genome's data by adding a random integer from
            `-sigma` to `+sigma`. If `sigma` is not an `int`, the random is
            done from `sigma[0]` to `sigma[-1]` including both ends. The value
            may overflow or underflow but it will not affect any surrounding
            data.

            If `part` is left empty, every bytes of data may be affected. To
            restrict mutations to an area, you must precise an iterable of
            ranges (iterables) from which the destination will be chosen. If
            `bound` contains raw integers or raw string, they are interpreted
            as partition identifiers and thus replace by their partition's
            range.
        """
        if isinstance(sigma, int):
            sigma = (-sigma, +sigma)

        total = 0

        if not part:
            part = [range(self.size)]
            total = self.size
        else:
            for k in range(len(part)):
                if isinstance(part[k], (int, str)):
                    part[k] = self.partition[part[k]]
                total+= len(part[k])

        total = int(ratio * total)

        pr = grom.util.Progress("Mutation", total)
        for r in part:
            for c in range(int(ratio * len(r))):
                k = grom.util.randit(r, self.rand)
                new = self.data[k] + self.rand.randint(sigma[0], sigma[-1])
                self.data[k] = new % 0x100

                pr.update()
        del pr

        return self

    def geneswap(self, amount, maxSize, part=[]):
        """ Swaps random chunks of data.

            `amount` is the number of times the algorithm will be executed.

            Determines two areas of the `data`, of max size `maxSize` (in bytes)
            and within `part` then swap them.

            If `part` is left empty, every bytes of data may be affected. To
            restrict mutations to an area, you must precise an iterable of
            ranges (iterables) from which the destination will be chosen. If
            `bound` contains raw integers or raw string, they are interpreted
            as partition identifiers and thus replace by their partition's
            range.
        """
        if not part:
            part = [range(self.size)]
        else:
            for k in range(len(part)):
                if isinstance(part[k], (int, str)):
                    part[k] = self.partition[part[k]]

        pr = grom.util.Progress("Gene swapping", amount)
        for k in range(amount):
            r1 = grom.util.randit(part, self.rand)
            r2 = grom.util.randit(part, self.rand)

            s = min((len(r1) - 1, len(r2) - 1, maxSize))

            p1 = grom.util.randit(r1[:-s] or [r1[0]])
            p2 = grom.util.randit(r2[:-s] or [r2[0]])

            tmp = self.data[p1:p1 + s]
            self.data[p1:p1 + s] = self.data[p2:p2 + s] 
            self.data[p2:p2 + s] = tmp

            pr.update(k)
        del pr

        return self

    def apply(self, do, part, groupBy=1):
        """ Apply a function to the data.

            Run through the partitions and replace the value in the data with
            the value returned from calling the function `do`, provided with
            the current data.

            If `part` is left empty, every bytes of data may be affected. To
            restrict mutations to an area, you must precise an iterable of
            ranges (iterables) from which the destination will be chosen. If
            `bound` contains raw integers or raw string, they are interpreted
            as partition identifiers and thus replace by their partition's
            range.

            If `groupBy` is not 1 (default value) the function `do` will
            receive a `bytearray` of size `groupBy` and must return a
            `bytearray` of the same size to replace into the data. Note: if
            there is less than `groupBy` bytes of data left to process, the
            object passed to `do` will still by a `bytearray` the size of
            `groupBy` with unused bytes filled with `0x00` and only the needed
            bytes from the returned `bytearray` will by used.
        """
        if not part:
            part = [r for n, r in self.partition]
        else:
            for k in range(len(part)):
                if isinstance(part[k], (int, str)):
                    part[k] = self.partition[part[k]]

        pr = grom.util.Progress("Applying", len(part))
        for r in part:
            for k in range(r[0], r[-1] + 1, groupBy):
                if groupBy == 1:
                    self.data[k] = do(self.data[k])
                else:
                    st, ed = k, k + groupBy
                    if ed < self.size + 1:
                        self.data[st:ed + 1] = do(self.data[st:ed + 1])
                    else:
                        off = ed - self.size
                        data = self.data[st:self.size] + bytearray([0] * off)
                        self.data[st:self.size] = do(data)[:groupBy - off]
        del pr

        return self

    def crossover(self, mate, name=None, rand=None, part=[], crosser=None):
        """ Create a crossover `Genome` from parents.

            `self` and `mate` are crossed over into a new `Genome`. This
            algorithm is not yet finished, and only for testing and
            placeholding purposes. `amount` is the number of times the
            algorithm will be executed.

            For each given bound, determines (randomly) which chunk of data
            (from eight parent) will go into the new `Genome`. The `part`
            parameters should be a full and flawless (no holes, no overlaps)
            partition for the data. Both parent should have the same size.
            Note that none of this is checked here as of right now.

            If the `crosser` function is not `None`, it is called with for
            parameters the two chunks of data to swap as `bytearray`s (`self`
            first, then `mate`) along with the name of the current bound index,
            and expected an output of data the same size, formatted as on of:
            `int[]` `bytes` `str` (supposedly 'ascii' encoded) or `bytearray`.
            The new `Genome`'s data is initialized at `self.data`, therefore if
            `crosser` does not return an appropriated result, the partition will be
            kept at this value.

            If not name is given, the name will be "`self.name`x`mate.name`".

            If the `rand` is not given, the new `Genome` will generate its own.

            If `part` is left empty, it will be loaded from the partition
            system of this `Genome` (`self`). To restrict mutations to an area,
            you must precise an iterable of ranges (iterables) from which the
            destination will be chosen. If `bound` contains raw integers or raw
            string, they are interpreted as partition identifiers and thus
            replace by their partition's range. Note that `mate`'s partition is
            never taken into account.

            Lastly, only `self`'s random is used.
        """
        if not part:
            part = [r for n, r in self.partition]
        else:
            for k in range(len(part)):
                if isinstance(part[k], (int, str)):
                    part[k] = self.partition[part[k]]

        data = bytearray(self.data)

        pr = grom.util.Progress("Crossing over", len(part))
        for k in range(len(part)):
            st, ed = part[k][0], part[k][-1]

            if callable(crosser):
                r = crosser(self.data[st:ed + 1], mate.data[st:ed + 1], k)

                if isinstance(r, str):
                    r = bytearray(r, 'ascii')
                if isinstance(r, (bytes, list, tuple)):
                    r = bytearray(r)
            else:
                which = grom.util.randit((self.data, mate.data), self.rand)
                r = which[st:ed + 1]

            data[st:ed + 1] = r

            pr.update(k)
        del pr

        return Genome(data, name or self.name + "x" + mate.name, rand, True)

    def select(self, part, filler=None):
        """
        """
        if not part:
            part = [r for n, r in self.partition]
        else:
            for k in range(len(part)):
                if isinstance(part[k], (int, str)):
                    part[k] = self.partition[part[k]]

        data = bytearray([filler])*self.size if filler != None else bytearray()

        pr = grom.util.Progress("Selecting", len(part))
        for k in range(len(part)):
            st, ed = part[k][0], part[k][-1]

            if filler != None:
                data[st:ed + 1] = self.data[st:ed + 1]
            else:
                data+= self.data[st:ed + 1]

            pr.update(k)
        del pr

        return data
    # END data modification
