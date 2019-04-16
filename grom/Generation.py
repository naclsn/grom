import grom

class Generation:
    """ A `Generation` is `Genome` dictionary, that you can load and save from
        an archive, and is designed to ease `Genome` mass manipulation.
    """
    # START object general
    def __init__(self, genomes={}):
        """ Not done yet!

            TODO: do.
        """
        self.genomes = genomes
        self.categories = []

    def __str__(self):
        """ Returns a _really basic_ representation.

            Concatenates the representations of every `Genome`s of this
            `Generation`.
        """
        return "\n---\n".join([str(g) for g in self])
    # END object general

    # START genome management
    def __getitem__(self, k):
        """ Gets the first `Genome` of name `k`.

            If multiple `Genome`s have exactly the same name, only the first
            one is returned, overshadowing any others.

            If `k` is a `list`, returns a list equivalent to calling the
            function for each name in `k`.

            If `k` is a `tuple`, the last value of `k` is the default value.

            If `k` is callable, returns the same as `Generation.select` with
            `k` as the `only` function.
        """
        if isinstance(k, list):
            return [self[n] for n in k]

        if isinstance(k, tuple):
            return self.genomes.get(k[0], k[-1])

        if callable(k):
            return self.select(k)

        return self.genomes[k]

    def __len__(self):
        """ Returns the number of `Genome` for the `Generation`.
        """
        return len(self.genomes)

    def __iter__(self):
        """ Iterates over the `Genome`s of this `Generation`
        """
        return self.genomes

    def categorise(self, delimiter):
        """ Delimits the `Generation` into categories.

            The `delimiter` function does not need to necessarily return an
            integer for the categories, but it should have the same output for
            two `Genome` of the same categories.

            Note: maybe this function and the variables surrounding it needs to
            be reworks...
        """
        cat = {}

        pr = grom.util.Progress("Categorizing", len(self.genomes))
        for e in self:
            k = delimiter(e)

            if not k in cat.keys():
                cat[k] = len(self.categories)
                self.categories.append([e])
            else:
                self.categories[cat[k]].append(e)

            pr.update()
        del pr

        return self

    def select(self, only):
        """ Selects `only` some `Genome`s.

            Returns a list of all `Genome` returning `True` (or any Python
            not-`Fales` equivalents) through the `only` function:
            ```
            only(currentGenome:Genome):bool
            ```
        """
        return [g for g in self if only(g)]

    def foreach(self, do, only=None):
        """ Classic for-each loop.

            Iterates over each `Genome` and apply the `do` function:
            ```
            do(currentGenome:Genome):T
            ```

            If `only` is provided, apply on the return of `Generation.select`.
            For more details on the `only` parameter, see `Generation.select`.

            Returns a dictionary mapping the `Genome`'s name to `do`'s output.
        """
        w = self.select(only) if only else self
        return dict([(g.name, do(g)) for g in w])

    def aggregate(self, do, start=None, only=None):
        """ Classic aggregation function.

            Iterates over each `Genome`, passing and getting an accumulator
            through `do` (`start` is the initial value):
            ```
            do(currentValue:T, currentGenome:Genome):T
            ```

            If `only` is provided, apply on the return of `Generation.select`.
            For more details on the `only` parameter, see `Generation.select`.

            Returns the last value of the accumulator.
        """
        for g in self.select(only) if only else self:
            start = do(start, g)
        return start
    # END genome management

    # START mass data modification
    """ Nothing to implement yet...

        For function from `Genome`, use `Generation.foreach`:
        ```python
        G.foreach(lambda g: Genome.mutate(g, .001, 1), selectionFunction)
        ```
    """
    # END mass data modification
