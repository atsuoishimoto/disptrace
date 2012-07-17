
from memento import MementoMetaclass
import ast

class CodeManager(object):
    """
    Holder for compiled Python modules. Instance creation highly cached.
    """
    __metaclass__ = MementoMetaclass

    def __init__(self, filepath):
        self.filepath = filepath
        self.source = open(filepath).read()
        self.sourcelines = [ None ] + self.source.splitlines()
        try:
            self.ast = ast.parse(self.source)
        except StandardError:
            self.ast = None