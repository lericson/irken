"""CTCP decoding, encoding and dispatching."""

from irken.dispatch import DispatchRegistering, Command, handler

# This implementation is sort of taken from irssi. It isn't made based on the
# RFC, because the RFC is old and it never happened.
#
# It should perhaps be noted that irssi only thinks CTCP messages are ones
# starting and ending in 0x01, and CTCP replies are anything starting with
# 0x01, and having a 0x01 somewhere in it - and whatever might come after isn't
# regular text to be cared about.

class CTCPFormatError(ValueError): pass

_mq_map = (("\x16\x16", "\x16"), ("\x160", "\0"),
           ("\x16n", "\n"), ("\x16r", "\r"))

def quote_middle(data):
    r"""Middle-level quote data.

    This is the M-QUOTE part that the RFC speaks of.

    >>> quote_middle("Hi \x16!\r\n\x00")
    'Hi \x16\x16!\x16r\x16n\x160'
    >>> quote_middle("")
    ''
    """
    for x, y in _mq_map:
        data = data.replace(y, x)
    return data

def unquote_middle(data):
    r"""Middle-level unquote data.

    Breaks the RFC a little by not dropping unknown quotes.

    >>> unquote_middle("Hi \x16\x16!\x16r\x16n\x160")
    'Hi \x16!\r\n\x00'
    >>> unquote_middle("")
    ''
    """
    for x, y in _mq_map:
        data = data.replace(x, y)
    return data

def quote_ctcp(data):
    r"""CTCP-level quote data.

    This is for the X-QUOTE part that the RFC speaks of.

    >>> print quote_ctcp("\x01CTCP \\'fun\\'.\x01")
    \aCTCP \\'fun\\'.\a
    """
    for qc, dst in zip("\\\x01", "\\a"):
        data = data.replace(qc, "\\" + dst)
    return data

def unquote_ctcp(data):
    r"""CTCP-level unquote data.

    Same issue as unquote_middle.

    >>> unquote_ctcp("\\aCTCP \\\\'fun\\\\'.\\a")
    "\x01CTCP \\'fun\\'.\x01"
    """
    for qc, dst in zip("a\\", "\x01\\"):
        data = data.replace("\\" + qc, dst)
    return data

def split(data):
    r"""Split CTCP data into command^Wtag and arguments.

    >>> split("HELLO World!")
    ('HELLO', 'World!')
    >>> split("HELLO \\\\World\\\\!")
    ('HELLO', '\\World\\!')
    >>> split("\\aHELLO\\a")
    ('\x01HELLO\x01', '')
    """
    # The RFC states that there must either be no tag or arguments, a sole tag,
    # or a tag and arguments.
    if not data:
        return ("", "")
    elif " " not in data:
        return (unquote_ctcp(data), "")
    else:
        return tuple(map(unquote_ctcp, data.split(" ", 1)))

def join(tag, data):
    rv = quote_ctcp(tag)
    if data:
        rv += " " + quote_ctcp(data)
    return rv

def parse(text):
    r"""Parse CTCP segments out of *text*.

    >>> list(parse("Pre \x01TEST BATMAN!\x01 post"))
    [('TEST', 'BATMAN!')]
    >>> list(parse("Pre \x01TEST\x01\x01ROLF\x01 post"))
    [('TEST', ''), ('ROLF', '')]
    >>> list(parse("Pre \x01TEST\x01 Mid \x01ROLF\x01 post"))
    [('TEST', ''), ('ROLF', '')]
    >>> list(parse("Pre - post"))
    []
    """
    delim_l, delim_r = -1, -1
    while True:
        delim_l = text.find("\x01", delim_r + 1)
        delim_r = text.find("\x01", delim_l + 1)
        if -1 in (delim_l, delim_r):
            break
        yield split(unquote_middle(text[delim_l + 1:delim_r]))

class BaseCTCPDispatchMixin(DispatchRegistering):
    @handler("irc cmd privmsg", "irc cmd notice")
    def dispatch_ctcp(self, cmd, target, text):
        irc_cmd = cmd[8:].lower()
        tpnam = dict(privmsg="message", notice="reply")[irc_cmd]
        for tag, data in parse(text):
            args = (data,) if data else ()
            command = Command("ctcp %s %s" % (tpnam, tag), source=cmd.source)
            if not self.dispatch(command, *args):
                default_command = Command("ctcp " + tpnam + " default")
                self.dispatch(default_command, command, *args)

class CTCPDispatchMixin(BaseCTCPDispatchMixin):
    @handler("ctcp message version")
    def reply_to_version(self, cmd):
        self.send_ctcp(cmd.source.nick, "version", self.client_version, reply=True)

    def send_ctcp(self, target_name, cmd, data=None, reply=False):
        text = "\x01" + quote_middle(join(cmd, data)) + "\x01"
        command = "notice" if reply else "privmsg"
        self.send_cmd(None, command, (target_name, text))

if __name__ == "__main__":
    import doctest
    doctest.testmod()
