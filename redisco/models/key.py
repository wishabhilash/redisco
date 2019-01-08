try:
    str
except NameError:
    # Python 3
    str = str = str

class Key(str):
    def __getitem__(self, key):
        return Key("%s:%s" % (self, key))
