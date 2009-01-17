"""IRC parser."""

from irken.nicks import Mask

def parse_line(line, mask_maker=Mask.from_string):
    """Parse an IRC line, returning `(source, command, arguments)`.
    
    *source* is either None or a mask instance from *mask_maker*, if a prefix
    was given in the line.

    *command* is the IRC command specified in the line and is normalized to
    uppercase.
    
    *argument*s is a list of command arguments, and is the empty list if none
    were given.

    Note that this function shouldn't be given unicode instances, as the IRC
    protocol doesn't define any encoding and so works with byte streams rather
    than abstract text -- meaning `str` instances. That said, the result can be
    decoded safely if the encoding is known.

    >>> parse_line("HELLO")
    (None, 'HELLO', [])
    >>> parse_line(":Hello!world@example.net QUIT :Bored.")
    (Mask(ByteNickname('Hello'), 'world', 'example.net'), 'QUIT', ['Bored.'])
    >>> parse_line("PING ABC")
    (None, 'PING', ['ABC'])
    >>> parse_line("TEST :Hello :World :Bar")
    (None, 'TEST', ['Hello :World :Bar'])
    >>> parse_line(":Kidney@example.net SVERIGE ABC")
    (Mask(ByteNickname('Kidney@example.net')), 'SVERIGE', ['ABC'])
    """

    if line.startswith(":"):
        prefix, line = line[1:].split(" ", 1)
        source = mask_maker(prefix)
    else:
        source = None

    arguments = []
    if " " in line:
        command, args_raw = line.split(" ", 1)
        if args_raw.startswith(":"):
            trail = args_raw[1:]
            args_raw = None
        elif " :" in args_raw:
            args_raw, trail = args_raw.split(" :", 1)
        else:
            trail = None
        if args_raw is not None:
            arguments = args_raw.split(" ")
        else:
            arguments = []
        if trail is not None:
            arguments.append(trail)
    else:
        command = line

    return source, command.upper(), arguments

def build_line(source, command, arguments):
    """Build an IRC line from *prefix*, *command* and *arguments*.

    It is the inverse of *parse_line*, see that function's documentation for
    more information.

    >>> build_line(None, 'PING', ('World',))
    'PING World'
    >>> build_line(None, 'TOPIC', ('#example', ''))
    'TOPIC #example :'
    >>> build_line(*parse_line(":A!B@C ABC ABC :ABC ABC"))
    ':A!B@C ABC ABC :ABC ABC'
    >>> build_line(*parse_line("ABC ABC :ABC ABC"))
    'ABC ABC :ABC ABC'
    """

    r = ""
    if source:
        r += ":%s " % (source.to_string(),)
    r += command
    if arguments:
        r += " "
        # An empty argument can only correctly be represented as a
        # trailing argument with no content, thus it has to be the last
        # argument, too. This if catches both spaces in the last argument, and
        # empty last arguments and makes a trailing argument out of it.
        if " " in arguments[-1] or not arguments[-1]:
            if len(arguments) > 1:
                r += " ".join(arguments[:-1]) + " "
            r += ":" + arguments[-1]
        # Otherwise proceed like always, by joining all arguments with a
        # nice-looking space.
        else:
            r += " ".join(arguments)
    return r

def is_numeric(v):
    """Returns True if v is an IRC numeric, False otherwise.

    >>> is_numeric("301")
    True
    >>> is_numeric("30")
    False
    >>> is_numeric("ABC")
    False
    """
    return len(v) == 3 and v.isdigit()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
