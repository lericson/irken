import logging
from irken import UnhandledCommandError
from types import MethodType

logger = logging.getLogger("irken.dispatch")

def handler(*commands):
    def deco(f):
        f.handles_commands = commands
        return f
    return deco

class DispatchRegisteringType(type):
    """Type for dispatch registering classes.

    Essentially all it does is add or update an event table on the classes of
    its type. It looks for any function that has a `handles_commands` attribute
    and is callable.
    """

    def __new__(cls, name, bases, attrs):
        evtable = attrs.setdefault("base_evtable", {})
        attr_names = attrs.keys()
        super_cls = super(DispatchRegisteringType, cls)
        new_cls = super_cls.__new__(cls, name, bases, attrs)
        for attr_name in attr_names:
            attr = getattr(new_cls, attr_name)
            if callable(attr) and hasattr(attr, "handles_commands"):
                for cmd in attr.handles_commands:
                    evtable.setdefault(cmd.lower(), []).append(attr)
        return new_cls

class DispatchRegistering(object):
    """Base class for dispatch registering.

    Takes the event table from the type and updates it with instance-specific
    modifications (given as the `evtable` kwarg at construction.)

    It also converts unbound methods to bound, so that there's one single call
    structure to use.
    """

    __metaclass__ = DispatchRegisteringType

    def __init__(self, *args, **kwds):
        evtable = self.base_evtable.copy()
        if "evtable" in kwds:
            evtable.update(kwds.pop("evtable"))
        for cmd, handlers in evtable.iteritems():
            for idx, handler in enumerate(handlers):
                if isinstance(handler, MethodType):
                    handlers[idx] = MethodType(handler, self, self.__class__)
        self.evtable = evtable
        super(DispatchRegistering, self).__init__(*args, **kwds)

    def dispatch(self, command, *args, **kwds):
        for handler in self.evtable.get(command.lower(), ()):
            yield handler(*args, **kwds)

# irken mixins

class SimpleDispatchMixin(DispatchRegistering):
    """Dispatches received commands to specified methods."""

    def recv_cmd(self, prefix, command, args):
        numeric = command.isdigit() and len(command) == 3
        handlers = self.evtable.get(command.lower())
        # Select default handler if necessary.
        if not handlers:
            if numeric:
                handlers = (self.handle_default_numeric,)
            else:
                handlers = (self.handle_default_command,)
        for handler in handlers:
            try:
                handler(prefix, args)
            except:
                self.handle_error()

    # Non-fatal if numeric.
    def handle_default_numeric(self, numeric, prefix=None, *args):
        logger.info("unhandled numeric %s", numeric)
    # Fatal if non-numeric.
    def handle_default_command(self, prefix, args):
        raise UnhandledCommandError(command)

    def handle_error(self):
        logger.exception("command dispatch")

class CommonDispatchMixin(SimpleDispatchMixin):
    """Redispatches rawer calls into more useful ones."""

    @handler("privmsg")
    def on_privmsg(self, prefix, args):
        pass

    @handler("nick")
    def on_nick(self, prefix, args):
        new_nick, = args
        if self.nick == nickname(prefix[0]):
            self._nick = new_nick

    @handler("ping")
    def on_ping(self, prefix, args):
        self.send_cmd(None, "PONG", args)
