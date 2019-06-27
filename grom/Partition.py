import grom

class Partition:
    """ Finally a class for the partition system!
    """
    def __init__(self, size, partition=[], parser=None):
        # TODO: list members
        """ Create a partition. TODO: redo

            Bind a partition system to the data as described by `part`. It
            should be an array of `(str, range)` tuples.

            If the last element of the tuple is an `int` (i.e. `(str, int)`),
            this value indicate the end of the range which starts at the end of
            the previous one (or 0 if none). (The value should be the first
            address not to include!)

            If the last tuple does not implement a `range` (i.e. is only made
            of a name), it will be assigned what is left of the data.

            Note: This function does not check for overlaps nor unmapped areas.
            If two partitions have the same name, the function `Genome.idof`
            will only returns the later one. In that case, you may not use the
            name as an identifier, but rather the number.
        """
        self.size = size

        if not partition:
            partition = [("default", range(self.size))]

        if isinstance(partition, list):
            self.partition = partition.copy()
            self.pmap = dict()

            for k in range(len(self)):
                if isinstance(self.partition[k][1], int):
                    st = self.partition[k-1][1][-1] if k else 0
                    ed = self.partition[k][1] + 1
                    self.partition[k] = (self.partition[k][0], range(st, ed))

                if isinstance(self.partition[k], str):
                    self.pmap[self.partition[k]] = k
                else:
                    self.pmap[self.partition[k][0]] = k

            if isinstance(self.partition[-1], str):
                st = self.partition[-2][1][-1] if 1 < len(self) else 0
                r = range(st, self.size)
                self.partition[-1] = (self.partition[-1], r)

        else:
            self.load(partition, parser) # TODO: hum..?

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

        infos = "Partition size: {:,}b\n".format(self.size)
        names = "\n"
        parts = "|"

        pr = grom.util.Progress("Printing", len(self))
        for k in range(len(self)):
            n = int(len(self.partition[k][1]) * m - 1 - pushed)
            if n < 0:
                pushed+= n

            names+= "\n{}: {} ({:,}b | from Ox{:X} to 0x{:X})".format(
                    k,
                    self.partition[k][0],
                    len(self.partition[k][1]),
                    self.partition[k][1][0],
                    self.partition[k][1][-1]
                )
            parts+= str(k) + "-" * n + "|"

            pr.update(k)
        del pr

        return infos + parts + names

    def load(self, file, parser, comments=';'):
        """
            Gives you 1 line lookahead.
            (name, range(start, end)) = parser(currentLine, nextLine)
        """
        if isinstance(file, str):
            file = open(file, 'r')

        self.partition = []
        self.pmap = dict()

        lines = file.readlines()
        lineCurr, lineNext = "", ""

        pr = grom.util.Progress("Loading system", len(lines))
        for line in lines:
            line = line.split(comments)[0].strip()
            if line:
                lineCurr = lineNext
                lineNext = line

                if lineCurr:
                    self.partition.append(parser(lineCurr, lineNext))
                    self.pmap[self.partition[-1][0]] = len(self.partition) - 1

            pr.update()
        del pr

        return self

    def __getitem__(self, k):
        """ Returns the partition `k`'s `range`.

            If `k` is a `str`, return the partition of name `k`'s `range`.
        """
        return self.partition[self.idof(k) if isinstance(k, str) else k][1]

    def __setitem__(self, k, v):
        """ Rename the partition `k`.

            If `k` is a `str`, rename the partition previously named `k`.

            To change a partition size, you may use `Partition.resize`.
        """
        if isinstance(k, str):
            k = self.idof(k)
        self.partition[k] = (self.partition[k][0], v)

    def __len__(self):
        """ Returns the number of partition for the data.
        """
        return len(self.partition)

    def __iter__(self):
        """ Iterates over the partition system of this `Genome`.
        """
        return iter(self.partition)

    def idof(self, n):
        return self.pmap[n]

    def check(self):
        """ Check the integrity of the partition. Quite slow.

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

        h_start, h_started, h_sum = 0, False, 0
        o_start, o_started, o_sum = 0, False, 0

        pr = grom.util.Progress("Checking", self.size)
        for k in range(self.size):
            count = len([1 for n, r in self.partition if k in r])

            if not count and not h_started:
                h_start = k
                h_started = True
            elif h_start - k and count and h_started:
                holes.append(range(h_start, k))
                h_started = False
                h_sum+= k - h_start

            if 1 < count and not o_started:
                o_start = k
                o_started = True
            elif o_start - k and count < 2 and o_started:
                overlaps.append(range(o_start, k))
                o_started = False
                o_sum+= k - o_start

            pr.update(k)
        del pr

        grom.util.output("not mapped: {:.3}%".format(h_sum / self.size))
        grom.util.output("overmapped: {:.3}%".format(o_sum / self.size))

        return holes, overlaps

    def __sub__(self, mate): # TODO: doc here
        if isinstance(mate, tuple):
            k, v = mate
            if 0 < v:
                self.resize(k, 0, -v)
            else:
                self.resize(k, v, 0)

    def __add__(self, mate): # TODO: here too
        if isinstance(mate, tuple):
            k, v = mate
            if 0 < v:
                self.resize(k, 0, v)
            else:
                self.resize(k, -v, 0)

        # # TODO: on-place changes or return new?
        # if isinstance(mate, list):
        #     mate = Partition(mate, self.size) # TODO: note

        # # self.partition+= mate.part
        # # self.pmap.update(mate.pmap)

        # # return self
        # return Partition(self.partition + mate.part, self.size)

    def resize(self, k, before, after): # TODO: check
        """ Resizes a partition.

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
            self.partition[k - 1] = (self.partition[k - 1][0], \
                                     self.partition[k - 1][1][:-before])

        elif k + 1 < len(self):
            self.partition[k + 1] = (self.partition[k + 1][0], \
                                     self.partition[k + 1][1][after:])

        self.partition[k] = (self.partition[k][0], range(lower, upper))

        return self
