import logging
from irken import UnhandledCommandError
from irken.nicks import Mask
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
        # We create a new base_evtable based on the one base classae's.
        evtable = attrs.setdefault("base_evtable", {})
        for base in bases:
            if hasattr(base, "base_evtable"):
                evtable.update(base.base_evtable)
        super_cls = super(DispatchRegisteringType, cls)
        new_cls = super_cls.__new__(cls, name, bases, attrs)
        for attr in vars(new_cls):
            # We must use getattr to trigger the property machinery that gives
            # us unbound methods and that.
            val = getattr(new_cls, attr)
            if hasattr(val, "handles_commands"):
                for cmd in val.handles_commands:
                    evtable.setdefault(cmd.lower(), []).append(attr)
        return new_cls

class DispatchRegistering(object):
    """Base class for dispatch registering.

    Takes the event table from the class and updates it with instance-specific
    modifications, that is, the keyworg argument *evtable*.
    """

    __metaclass__ = DispatchRegisteringType

    def __init__(self, *args, **kwds):
        self.evtable = evtable = self.base_evtable.copy()
        self.evtable.update(kwds.pop("evtable", {}))
        return super(DispatchRegistering, self).__init__(*args, **kwds)

    def handlers_for(self, command):
        for handler_attr in self.evtable.get(command.lower(), ()):
            yield getattr(self, handler_attr)

class Command(unicode):
    def __new__(cls, command, source=None):
        return super(Command, cls).__new__(cls, command)
    
    def __init__(self, command, source=None):
        super(Command, self).__init__(command)
        self.source = source

    def __repr__(self):
        r = super(Command, self).__repr__()
        return self.__class__.__name__ + "(%s, source=%r)" % (r, self.source)

# irken mixins

class SimpleDispatchMixin(DispatchRegistering):
    """Dispatches received commands to specified methods."""

    def recv_cmd(self, prefix, command, args):
        numeric = command.isdigit() and len(command) == 3
        handlers = self.handlers_for(command)
        # Select default handler if necessary.
        if not handlers:
            if numeric:
                handlers = (self.handle_default_numeric,)
            else:
                handlers = (self.handle_default_command,)
        
        info = Command(command, source=self.lookup_prefix(prefix))
        for handler in handlers:
            try:
                handler(info, *args)
            except:
                self.handle_error()

    # Non-fatal if numeric.
    def handle_default_numeric(self, info, *args):
        logger.info("unhandled numeric %s", info["command"])
    # Fatal if non-numeric.
    def handle_default_command(self, info, *args):
        raise UnhandledCommandError(info["command"])

    def handle_error(self):
        logger.exception("command dispatch")

class CommonDispatchMixin(SimpleDispatchMixin):
    """Redispatches rawer calls into more useful ones."""

    # TODO: Complete
    @handler("privmsg")
    def dispatch_privmsg(self, cmd, target_name, text):
        target = self.lookup_prefix(target_name)
        if self == target:
            pass # TODO Handle private queries.
        else:
            pass # TODO Handle public messages.

    @handler("nick")
    def update_own_nick(self, cmd, new_nick):
        if self == cmd.source:
            self._nick = new_nick

    @handler("ping")
    def reply_to_ping(self, cmd, *args):
        self.send_cmd(None, "PONG", args)
