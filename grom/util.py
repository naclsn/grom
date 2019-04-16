""" Helper function and class, global settings.

    You can import and reset `DEBUG` to get force the appearance of progress
    bar (or remove them despite `__debug__`...).
"""

import random
import os

DEBUG = __debug__
LINE_SIZE = 80

def output(info, end="\n"):
    """ Console output function.

        Mainly used for debugging purposes. You can prevent it from printing by
        resetting `grom.util.DEBUG` to `False`.
    """
    if DEBUG:
        print(info, end=end)

def randit(it, rand=None):
    """ Random object from iterable.

        Return an occurrence at random from the given iterable, using `rand` if
        given or else a new `Random` object.
    """
    return it[(rand or random.Random()).randrange(0, len(it))]

class Progress:
    """ A progress bar.

        The `Progress` object is meant to be initialized with a message and a
        final value to reach (for example the number of iteration of a loop).
        You can then `update` it with the current value of progress until the
        task is finished. After what you are supposed to delete the object
        using `del ` to finish the progress bar.
    """
    def __init__(self, message, final=1):
        """ Initialises the progress bar.

            Display the message and the '[' of the progress bar. `final` should
            be at least the maximal value you will pass to `update`.
        """
        self.final = final
        self.progress = 0

        self.av = 0

        output(message + "..", end="")
        output(" " * (16 - len(message)), end="[")

    def update(self, av=-1):
        """ Updates the progress bar.

            Add the correct count of '=' in regard to the `final` value given
            and the `av` parameter: it should be lower than `final`, but higher
            than any previously given value to `av` (or greater than `0` if you
            have not called `update` yet).

            If you have no idea what the value of `av` should be or you are
            using a for-each loop, you can call `update` with no parameters:
            progress will go by 1 by default.
        """
        if av < 0:
            av = self.av + 1

        newProgress = int(av / self.final * (LINE_SIZE - 19))
        if self.progress < newProgress:
            output("=" * (newProgress - self.progress), end="")
            self.progress = newProgress

        self.av = av

    def __del__(self):
        """ Finishes the progress bar.

            Output the missing '=' if any, then the ']' to end the line at
            `grom.util.LINE_SIZE` characters. You should call this function
            using the built-in `del ` directive [?].
        """
        output("=" * (LINE_SIZE - 18 - self.progress) + "]")
