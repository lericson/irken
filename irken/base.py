import logging
from irken.parser import parse_line, build_line
from irken.nicks import nickname

logger = logging.getLogger("irken.base")

class BaseConnection(object):
    """Very basic connection.

    This essentially knows how to parse IRC data and build lines. It doesn't
    know /how/ to send, or how to dispatch, and so on, but it does know that
    it should send etc.
    """

    def __init__(self, nick):
        self.nick = nick

    def parse_line(self, line):
        return parse_line(line)

    def build_line(self, prefix, command, args):
        return build_line(prefix, command, args)

    def send_cmd(self, prefix, command, args):
        """Send an IRC command."""
        line = self.build_line(prefix, command, args)
        logger.debug("send " + repr(line))
        self.send_raw(line + "\r\n")

    def send_raw(self, line):
        """Send raw IRC data.

        This is what takes care of actually putting the data on the network.
        """
        raise NotImplementedError("io mixin")

    def recv_cmd(self, prefix, command, args):
        """Receive an IRC command."""
        raise NotImplementedError("dispatch mixin")

    def recv_raw(self):
        """Read raw IRC data."""
        raise NotImplementedError("io mixin")

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

    def run_once(self):
        self.recv_raw()

    def run_forever(self):
        while True: self.run_once()

# The distinction between BaseConnection and Connection lies in that the
# base itself doesn't know any specifics.

class Connection(BaseConnection):
    def _set_nick(self, value):
        value = nickname(value)
        if hasattr(self, "_nick"):
            if value != self.nick:
                self.send_cmd(None, "NICK", (value,))
        else:
            self._nick = value
    def _get_nick(self): return getattr(self, "_nick", "*")
    nick = property(_get_nick, _set_nick)
