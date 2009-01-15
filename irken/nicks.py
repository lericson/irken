r"""Nickname types.

There are two types, representing the two Python string types:
 - ByteNickname: a nickname in plain, raw form - it is not interpreted into
                 any abstract sense of code points, and is a byte string.
 - UniNickname:  a nickname in abstract character form - this is the preferred
                 form.

They both convert the special IRC nickname characters to and fro correctly for
upper- and lowercasing. This means that you can compare nicknames like you
expect to:

>>> nickname("foo[]").lower() == nickname("foo{}").lower()
True

The nickname factory function is for awesome. It's actually for making either a
ByteNickname or UniNickname depending on the input value -- str gives
ByteNickname, and unicode gives UniNickname.

>>> nickname("foo")
ByteNickname('foo')
>>> nickname(u"foo")
UniNickname(u'foo')

That said, you can convert between the two:

>>> UniNickname(nickname("foo"))
UniNickname(u'foo')
>>> ByteNickname(nickname(u"foo"))
ByteNickname('foo')
>>> nickname(u"\xe5").encode("utf-8")
ByteNickname('\xc3\xa5')
>>> nickname("\xc3\xa5").decode("utf-8")
UniNickname(u'\xe5')

Everything you'd expect to give a new *Nickname instance does!
>>> nickname("hoLLa").swapcase()
ByteNickname('HOllA')
>>> nickname("test").title()
ByteNickname('Test')
>>> nickname("test").zfill(10)
ByteNickname('000000test')
>>> nickname("--test--").strip("-")
ByteNickname('test')
>>> nickname("--test--").rstrip("-")
ByteNickname('--test')
>>> nickname("--test--").lstrip("-")
ByteNickname('test--')

They work individually very well.

>>> ByteNickname("foo")
ByteNickname('foo')
>>> ByteNickname("foo").upper()
ByteNickname('FOO')
>>> ByteNickname("foo[]").upper()
ByteNickname('FOO{}')
>>> ByteNickname("FOO{}").lower()
ByteNickname('foo[]')
>>> ByteNickname("Foo bar")
Traceback (most recent call last):
  ...
ValueError: invalid nickname: 'Foo bar'

>>> UniNickname("foo")
UniNickname(u'foo')
>>> UniNickname("foo").upper()
UniNickname(u'FOO')
>>> UniNickname("foo[]").upper()
UniNickname(u'FOO{}')
>>> UniNickname("FOO{}").lower()
UniNickname(u'foo[]')
>>> UniNickname("Foo bar")
Traceback (most recent call last):
  ...
ValueError: invalid nickname: 'Foo bar'
"""

import string

special_lc = "[]\\"
special_uc = "{}|"

def is_valid_nickname(nick):
    """Loosely check if *nick* is a valid nickname."""
    return bool(nick) and not any(ord(c) <= 32 for c in nick)

class BaseNickname(basestring):
    def __new__(cls, val=""):
        if not is_valid_nickname(val):
            raise ValueError("invalid nickname: %r" % (val,))
        return super(BaseNickname, cls).__new__(cls, val)

    def __repr__(self):
        real_repr = super(BaseNickname, self).__repr__()
        return "%s(%s)" % (self.__class__.__name__, real_repr)

    # TODO Make this less ugly.
    def lower(self):
        rv = super(BaseNickname, self).lower()
        return nickname(rv.translate(self._uc_lc))

    def upper(self):
        rv = super(BaseNickname, self).upper()
        return nickname(rv.translate(self._lc_uc))

    def swapcase(self):
        rv = super(BaseNickname, self).swapcase()
        return nickname(rv.translate(self._swapc))

    def converter(name):
        def inner(self, *args, **kwds):
            rv = getattr(super(BaseNickname, self), name)(*args, **kwds)
            return nickname(rv)
        return inner

    encode = converter("encode")
    decode = converter("decode")
    translate = converter("translate")
    title = converter("title")
    zfill = converter("zfill")
    strip = converter("strip")
    rstrip = converter("rstrip")
    lstrip = converter("lstrip")

    del converter

class ByteNickname(BaseNickname, str):
    _lc_uc = string.maketrans(special_lc, special_uc)
    _uc_lc = string.maketrans(special_uc, special_lc)
    _swapc = string.maketrans(special_lc + special_uc, special_uc + special_lc)

class UniNickname(BaseNickname, unicode):
    # Don't ask me why Python thinks it's a great idea to have Unicode
    # _ordinals_ in the mappings.
    _lc_uc = dict((ord(k), ord(v)) for (k, v) in zip(special_lc, special_uc))
    _uc_lc = dict((ord(k), ord(v)) for (k, v) in zip(special_uc, special_lc))
    _swapc = dict(_lc_uc, **_uc_lc)

def nickname(val):
    if isinstance(val, str):
        return ByteNickname(val)
    else:
        return UniNickname(val)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
