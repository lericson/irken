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
        2. encode the potential prefix with set encoding,
        3. encode the potential arguments with set encoding,
        4. emit.

    And the reverse on ingress:
        1. Parse,
        2. decode the command as ASCII data,
        3. decode the potential prefix with set encoding,
        4. decode the potential arguments with set encoding.

    The actual emission and parsing isn't done here: it's done the exact same
    way as the base does. Because that's expected.

    >>> em = EncodingMixin()
    >>> em._decode_seq(em._encode_seq((u"\xe5", u"Hi!")))
    [u'\xe5', u'Hi!']
    >>> em._encode_seq(em._decode_seq(("\xc3\xa5", "Hi!")))
    ['\xc3\xa5', 'Hi!']
    """

    encoding = "utf-8"

    def send_cmd(self, prefix, command, args):
        return super(EncodingMixin, self).send_cmd(
            prefix and prefix.encode(self.encoding),
            command.encode("ascii"),
            args and self._encode_seq(args))

    def recv_cmd(self, prefix, command, args):
        return super(EncodingMixin, self).recv_cmd(
            prefix and prefix.decode(self.encoding),
            command.decode("ascii"),
            args and self._decode_seq(args))

    def _code_seq(self, target_type, seq):
        """Encode or decode sequence.

        If *target_type* is `unicode`, decodes.
        If *target_type* is `str`, encodes.
        """
        for v in seq:
            if not v:
                yield v
            elif isinstance(v, target_type):
                yield v
            elif issubclass(target_type, unicode):
                yield v.decode(self.encoding)
            elif issubclass(target_type, str):
                yield v.encode(self.encoding)
            else:
                raise ValueError("target_type = %r" % (target_type,))

    def _encode_seq(self, seq): return list(self._code_seq(str, seq))
    def _decode_seq(self, seq): return list(self._code_seq(unicode, seq))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
