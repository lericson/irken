class EncodingMixin(object):
    r"""Encoder/decoder.
    
    Takes care of encoding on egress,
                  decoding on ingress.

    The thing with IRC and encodings is that the actual IRC protocol tokens are
    in US-ASCII. Nothing else. IRC also defines its commands more or less as
    tokens in their own right. However, the prefix and arguments are commonly
    decoded by IRC clients.

    Therefore, the workflow at egress becomes:
        1. Encode the command as ASCII data,
        2. encode the potential prefix with set encoding(s),
        3. encode the potential arguments with set encoding(s),
        4. emit.

    And the reverse on ingress:
        1. Parse,
        2. decode the command as ASCII data,
        3. decode the potential prefix with set encoding(s),
        4. decode the potential arguments with set encoding(s).

    The actual emission and parsing isn't done here: it's done the exact same
    way as the base does. Because that's expected.

    >>> from irken.utils import DebugMixin
    >>> class DebugEncoding(EncodingMixin, DebugMixin): pass
    >>> em = DebugEncoding()
    >>> em._decode(em._encode(u"\xe5hej!"))
    u'\xe5hej!'
    >>> em._encode(em._decode("\xc3\xa5hej!"))
    '\xc3\xa5hej!'

    This is it relying on its secondary encoding.
    >>> em._decode("\xe5hej!")
    u'\xe5hej!'

    (There's no possible way to make a character that UTF-8 can't encode, but
    latin1 can. Is it possible to make characters that UTF-8 doesn't cover?)

    Test sending a command -- should encode to UTF-8 data.
    >>> em.send_cmd(u"hall\xe5an", "HELLO",
    ...             [u"I \xf6 r\xe5r yr \xe5l p\xe5 \xf6l"])
    ... # doctest: +NORMALIZE_WHITESPACE
    send: prefix='hall\xc3\xa5an', command=HELLO,
          args=['I \xc3\xb6 r\xc3\xa5r yr \xc3\xa5l p\xc3\xa5 \xc3\xb6l']

    Test receiving a command -- should decode from same UTF-8 data.
    >>> em.recv_cmd("hall\xc3\xa5an", "HELLO",
    ...             ["I \xc3\xb6 r\xc3\xa5r yr \xc3\xa5l p\xc3\xa5 \xc3\xb6l"])
    ... # doctest: +NORMALIZE_WHITESPACE
    recv: prefix=u'hall\xe5an', command=HELLO,
          args=[u'I \xf6 r\xe5r yr \xe5l p\xe5 \xf6l']

    Test receiving a latin1-encoded command.
    >>> em.recv_cmd("Willd", "PRIVMSG",
    ...             ["#common.people", "Jag \xe4r Shiva, d\xf6dsgudinnan."])
    ... # doctest: +NORMALIZE_WHITESPACE
    recv: prefix=u'Willd', command=PRIVMSG,
          args=[u'#common.people', u'Jag \xe4r Shiva, d\xf6dsgudinnan.']
    """

    # These are nice preset defaults for Europeans, and yes,
    # I'm a little ethnocentric. Or is it mere convenience?
    encodings = ("utf-8", "latin1")

    def send_cmd(self, prefix, command, args):
        if prefix: prefix = self._encode(prefix)
        command = command.encode("ascii")
        if args: args = map(self._encode, args)
        return super(EncodingMixin, self).send_cmd(prefix, command, args)

    def recv_cmd(self, prefix, command, args):
        if prefix: prefix = self._decode(prefix)
        command = command.decode("ascii")
        if args: args = map(self._decode, args)
        return super(EncodingMixin, self).recv_cmd(prefix, command, args)

    def _code(self, target_type, v):
        if isinstance(v, target_type):
            return v
        elif issubclass(target_type, str):
            exc_type = UnicodeEncodeError
            get_coded_value = v.encode
        elif issubclass(target_type, unicode):
            exc_type = UnicodeDecodeError
            get_coded_value = v.decode
        else:
            raise ValueError("target_type = %r" % (target_type,))

        excs = {}
        for encoding in self.encodings:
            try:
                return get_coded_value(encoding)
            except exc_type, exc_value:
                excs[encoding] = exc_value
                continue
        # I'm paranoid. I can't fathom how this would impact GC, yet I can't
        # avoid explicitly clearing the exception value mappings.
        excs_str = str(excs)
        excs.clear()
        raise exc_type("none of the encodings succeeded: %s" % excs_str)

    def _encode(self, v): return self._code(str, v)
    def _decode(self, v): return self._code(unicode, v)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
