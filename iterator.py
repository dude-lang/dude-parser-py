class Iterator:
    def __init__(self, iterable):
        self._pos = 0
        self._max = len(iterable) - 1
        self._list = iterable

    def __iter__(self):
        return iter(self._list)

    def __bool__(self):
        return 0 <= self._pos <= self._max

    def __getitem__(self, key):
        if isinstance(key, slice):
            l, r, s = key.start, key.stop, key.step
            return self._list[max(0, l):min(self._max, r)]
        elif isinstance(key, int):
            if 0 <= key <= self._max:
                return self._list[key]
            raise IndexError("Out of bounds")
        else:
            raise TypeError("Invalid argument type.")

    def pos(self):
        return self._pos

    def front(self):
        return self._list[:self._pos]

    def tail(self):
        return self._list[self._pos:]

    def slice(self, elements: int = 3):
        return self._list[self._pos - elements:self._pos + elements]

    def get(self):
        return self._list[self._pos]

    def peek(self, offset: int = 1):
        if self._pos == self._max:
            raise StopIteration

        return self._list[self._pos + offset]

    def next(self):
        self._pos += 1

        if not self:
            raise StopIteration

        return self.get()

    def prev(self):
        self._pos -= 1
        return self.get()

    def seek(self, pos: int):
        self._pos = pos

        if not self:
            raise StopIteration
