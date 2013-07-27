# -*- coding: utf-8 -*-
from collections import MutableMapping

class ModelDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.__data_storage = dict()
        self.__key_storage = dict()
        self.update(dict(*args, **kwargs))
        
    def __getitem__(self, key):
        return self.__data_storage[key.pk]
        
    def __setitem__(self, key, value):
        self.__data_storage[key.pk] = value
        self.__key_storage[key.pk] = key
        
    def __delitem__(self, key):
        del self.__data_storage[key.pk]
        del self.__key_storage[key.pk]
        
    def __len__(self):
        return len(self.__key_storage)
        
    def __iter__(self):
        return self.__key_storage.itervalues()

