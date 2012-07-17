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
