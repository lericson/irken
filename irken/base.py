import logging
from irken.nicks import Mask
from irken.parser import parse_line, build_line

logger = logging.getLogger("irken.base")

class BaseConnection(object):
    """Very basic connection.

    This essentially knows how to parse IRC data and build lines. It doesn't
    know /how/ to send, or how to dispatch, and so on, but it does know that
    it should send etc.
    """

    def __init__(self, nick):
        self.io = self.make_io()
        self.nick = nick
        self._prefix_cache = {}

    @property
    def mask(self):
        return Mask(self.nick)

    def __eq__(self, other):
        if hasattr(other, "nick"):
            return self.nick == other.nick
        return NotImplemented

    def connect(self, *args, **kwds):
        """Connect to something. This is outsourced to io."""
        return self.io.connect(*args, **kwds)

    def parse_line(self, line):
        return parse_line(line)

    def build_line(self, prefix, command, args):
        return build_line(prefix, command, args)

    def send_cmd(self, prefix, command, args):
        """Send an IRC command."""
        line = self.build_line(prefix, command, args)
        logger.debug("send " + repr(line))
        self.io.deliver(line + "\r\n")

    def recv_cmd(self, prefix, command, args):
        """Receive an IRC command."""
        raise NotImplementedError("dispatch mixin")

    def run(self, *args, **kwds):
        kwds.setdefault("consumer", self.consume)
        return self.io.run(*args, **kwds)

    def consume(self, data):
        """Consume every line in string *data*, returning any incomplete data
        found.

        This really just iterates through each line, parses it and calls
        `self.recv_cmd`.
        """
        lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        trail = lines.pop()
        for line in lines:
            logger.debug("recv " + repr(line))
            self.recv_cmd(*self.parse_line(line))
        return trail

    def lookup_prefix(self, prefix):
        """Turn *prefix* into an actual source with similar behavior to this
        instance itself.

        This default implementation does nothing smart, it's more of a factory
        with a cache than anything else. (Which means it wastes memory, yeah.)

        RemoteSource is used for unknowns, which is created through
        self.make_source. (So look there if you want to change stuff.)

        >>> from irken.tests import TestConnection
        >>> bc = TestConnection("self")
        >>> bc.lookup_prefix(("other",))
        <RemoteSource ('other',)>

        Though, if the mask looked up matches the instance's own nickname, then
        self is returned:

        >>> bc.lookup_prefix(("self",)) is bc
        True

        This is actually used for channels and other things as well (server
        names most notably), and a "source" is a very vague term by intent.

        >>> bc.lookup_prefix(("#im.a.channel",))
        <RemoteSource ('#im.a.channel',)>

        Regularly, this will be running on mask instances:

        >>> from irken.nicks import Mask
        >>> bc.lookup_prefix(Mask.from_string("self!foo@bar")) is bc
        True
        """
        # TODO There really should be some eviction strategy for entries in the
        # cache, but hey... Realistically, I can leak that memory.
        cache = self._prefix_cache
        key = prefix[0] if prefix else prefix
        if key == self.nick:
            return self
        if key not in cache:
            value = cache[key] = self.make_source(prefix)
            return value
        return cache[key]

    def make_source(self, prefix):
        return RemoteSource(prefix)

class RemoteSource(object):
    def __init__(self, mask):
        self.mask = mask
        # Could be a property, but it isn't.
        self.nick = mask[0] if mask else mask

    def __repr__(self):
        return "<RemoteSource %r>" % (self.mask,)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
