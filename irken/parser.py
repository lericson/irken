"""IRC parser."""

import re

# Strips off the prefix.
prefixed_line_re = re.compile(
    r"^:(?P<nickname>[^! ]+?)"
    r"(?:!(?P<username>[^@ ]+?)"
    r"(?:@(?P<hostname>[^ ]+?))?)? (?P<remainder>.+)$")

def parse_line(line):
    """Returns (source, command, arguments) where source can be None or
    a NickMask. arguments is a list of arguments, and can be empty.

    >>> parse_line("HELLO")
    (None, 'HELLO', [])
    >>> parse_line(":Hello!world@example.net QUIT :Bored.")
    (('Hello', 'world', 'example.net'), 'QUIT', ['Bored.'])
    >>> parse_line("PING ABC")
    (None, 'PING', ['ABC'])
    >>> parse_line("TEST :Hello :World :Bar")
    (None, 'TEST', ['Hello :World :Bar'])
    >>> parse_line(":Kidney@example.net SVERIGE ABC")
    (('Kidney@example.net', None, None), 'SVERIGE', ['ABC'])
    """

    prefix_mo = prefixed_line_re.search(line)
    if prefix_mo:
        stuff = prefix_mo.groups()
        source = stuff[:3]
        line = stuff[3]
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

    return source, command, arguments

def parse_lines(data):
    """Parses out all lines in data, returning an iterator of the lines
    that were parsed as well as the remnant data that wasn't a complete
    line.

    >>> parse_lines('HELLO\\nWorld.')[1]
    'World.'
    >>> parse_lines('')[1]
    ''
    >>> parse_lines('TEST\\nHELLO\\nWORLD\\n')[1]
    ''
    >>> parse_lines('TEST\\n\\nFOO\\nIncomplete')[1]
    'Incomplete'
    """

    lines = data.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    data = lines.pop()
    return (parse_line(line) for line in lines if line), data

def build_line(source, command, arguments):
    """Builds an IRC line from a prefix, command and arguments. See parse_line
    for a definition of what they can be.

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
        n_parts = len(source)
        r += ":" + source[0]
        if 3 >= n_parts >= 2:
            r += "!" + source[1]
            if n_parts == 3:
                r += "@" + source[2]
        elif n_parts > 3:
            raise ValueError(source)
        r += " "
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
