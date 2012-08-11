import ast 

class MementoMetaclass(type):
    """
    Classes that use this caching metaclass will have their instances
    automatically cached based on instantiation-time arguments (i.e. to __init__).
    Super-useful for not repetitively creating expensive-to-create objects.
    
    See http://code.activestate.com/recipes/286132-memento-design-pattern-in-python/
    """
    cache = {}

    def __call__(self, *args):
        key = (self, ) + args
        try:
            return self.cache[key]
        except KeyError:
            instance = type.__call__(self, *args)
            self.cache[key] = instance
            return instance
 
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


