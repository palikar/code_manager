import json



class CacheContainer:
    dirty = False

    def __init__(self, cache_file):
        self.file = cache_file
        
