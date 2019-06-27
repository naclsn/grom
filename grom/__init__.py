from grom.Genome import Genome
from grom.Partition import Partition
from grom.Generation import Generation
import grom.util as util

def debug(set):
    util.DEBUG = set

__all__ = ['Genome', 'Generation', 'Partition', 'debug']
