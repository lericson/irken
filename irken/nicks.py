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
    r"""Loosely check if *nick* is a valid nickname.
    
    >>> is_valid_nickname("foo")
    True
    >>> is_valid_nickname("foo bar")
    False
    >>> is_valid_nickname("foo\xff")
    True
    >>> is_valid_nickname("foo\0")
    False
    """
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
    """Convert *val* to a suitable nickname instance.

    >>> nickname("foo")
    ByteNickname('foo')
    >>> nickname(u"foo")
    UniNickname(u'foo')
    >>> nickname(nickname('foo'))
    ByteNickname('foo')
    """
    if isinstance(val, BaseNickname):
        return val
    elif isinstance(val, str):
        return ByteNickname(val)
    else:
        return UniNickname(val)

class Mask(tuple):
    r"""IRC mask.

    The mask must consist of at least a nickname, as is required to be useful
    at all. If a host is to be given, so must a username be.

    The nickname is converted into a suitable nickname instance using the
    `nickname` function.

    >>> m = Mask("foo")
    >>> m
    Mask(ByteNickname('foo'))
    >>> m.nick
    ByteNickname('foo')

    >>> m = Mask("foo", "bar", "baz")
    >>> m
    Mask(ByteNickname('foo'), 'bar', 'baz')
    >>> m.user, m.host
    ('bar', 'baz')

    >>> Mask("foo", host="baz")
    Traceback (most recent call last):
      ...
    TypeError: user must be given if host is

    The mask type also provides two utility methods for converting to and from
    the IRC mask representation::

        >>> Mask.from_string("foo!bar@baz")
        Mask(ByteNickname('foo'), 'bar', 'baz')
        >>> Mask.from_string(u"foo!bar@baz")
        Mask(UniNickname(u'foo'), u'bar', u'baz')
        >>> Mask("foo", "bar", "baz").to_string()
        'foo!bar@baz'
        >>> Mask(u"foo", u"bar", u"baz").to_string()
        u'foo!bar@baz'

    The parser even handles weird masks correctly::

        >>> # Not so weird - just has no host.
        >>> Mask.from_string("foo!bar")
        Mask(ByteNickname('foo'), 'bar')
        >>> # A little weirder, seemingly has no username but really only has
        >>> # nickname.
        >>> Mask.from_string("foo@baz")
        Mask(ByteNickname('foo@baz'))
        >>> # This actually has a weird nickname, and not any host at all.
        >>> Mask.from_string("foo@bar!baz")
        Mask(ByteNickname('foo@bar'), 'baz')

    As a matter of fact, it even does encoding and decoding::

        >>> Mask.from_string(u"\xe5bc").encode("utf-8")
        Mask(ByteNickname('\xc3\xa5bc'))
        >>> Mask.from_string("\xc3\xa5bc").decode("utf-8")
        Mask(UniNickname(u'\xe5bc'))

    Comparison works the way you'd expect it to, that is, it compares only the
    parts that are present in both masks::

        >>> mx = Mask.from_string("lericson")
        >>> my = Mask.from_string("lericson!lericson")
        >>> mx == my
        True
        >>> my = Mask.from_string("vishnu!lericson")
        >>> mx == my
        False
    """

    def __new__(cls, nick, user=None, host=None):
        if host and not user:
            raise TypeError("user must be given if host is")
        return super(Mask, cls).__new__(cls, (nick, user, host))

    def __init__(self, nick, user=None, host=None):
        super(Mask, self).__init__((nick, user, host))
        self.nick = nickname(nick)
        self.user = user
        self.host = host

    def __eq__(self, other):
        for c1, c2 in zip(self, other):
            if None in (c1, c2):
                break
            elif c1 != c2:
                return False
        return True

    def __repr__(self):
        parts = self.nick, self.user, self.host
        args = ", ".join(repr(part) for part in parts if part)
        return "%s(%s)" % (self.__class__.__name__, args)

    @classmethod
    def from_string(cls, val):
        args = ()
        for delim in "!@":
            if delim in val:
                part, val = val.split(delim, 1)
                args += (part,)
            else:
                break
        args += (val,)
        return cls(*args)

    def to_string(self):
        mapping = (("", self.nick),
                   ("!", self.user),
                   ("@", self.host))
        rv = ""
        for preceder, part in mapping:
            if part:
                rv += preceder + part
        return rv

    __str__ = __unicode__ = to_string

    def encode(self, coding, errors="strict"):
        return self.__class__.from_string(self.to_string().encode(coding))
    def decode(self, coding, errors="strict"):
        return self.__class__.from_string(self.to_string().decode(coding))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
