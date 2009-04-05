import logging
from irken import UnhandledCommandError
from irken.parser import is_numeric

logger = logging.getLogger("irken.dispatch")

def handler(*names):
    def deco(f):
        f.handles_names = names
        return f
    return deco

def evtable_extend(dst, src):
    for k in src:
        dst.setdefault(k, []).extend(src[k])

class DispatchRegisteringType(type):
    """Type for dispatch registering classes.

    Essentially all it does is add or update an event table on the classes of
    its type. It looks for any function that has a `handles_names` attribute
    and is callable.
    """

    def __new__(cls, name, bases, attrs):
        # We create a new base_evtable based on the one base classae's.
        evtable = attrs.setdefault("base_evtable", {})
        for base in bases:
            evtable_extend(evtable, getattr(base, "base_evtable", {}))
        super_cls = super(DispatchRegisteringType, cls)
        new_cls = super_cls.__new__(cls, name, bases, attrs)
        for attr in vars(new_cls):
            # We must use getattr to trigger the property machinery that gives
            # us unbound methods and that.
            val = getattr(new_cls, attr)
            if hasattr(val, "handles_names"):
                for name in val.handles_names:
                    evtable.setdefault(name.lower(), []).append(attr)
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

    def handlers_for(self, name):
        for handler_attr in self.evtable.get(name.lower(), ()):
            yield getattr(self, handler_attr)

    def dispatch(self, name, *args, **kwds):
        count = 0
        for handler in self.handlers_for(name):
            count += 1
            try:
                handler(name, *args, **kwds)
            except:
                if name != "dispatch error":
                    self.dispatch("dispatch error")
                else:
                    raise
        return count

    @handler("dispatch error")
    def handle_error(self, name):
        raise

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
        tpnam = "num" if is_numeric(command) else "cmd"
        command = Command("irc %s %s" % (tpnam, command),
                          source=self.lookup_prefix(prefix))
        if not self.dispatch(command, *args):
            self.dispatch("irc " + tpnam + " default", command, *args)

    # Non-fatal if numeric.
    @handler("irc num default")
    def note_missed_numeric(self, name, cmd, *args):
        logger.info("unhandled numeric %s", cmd)

    # Fatal if non-numeric.
    @handler("irc command default")
    def handle_default_command(self, name, cmd, *args):
        raise UnhandledCommandError(cmd)

    #def handle_error(self):
    #    logger.exception("command dispatch")

class CommonDispatchMixin(SimpleDispatchMixin):
    """Redispatches rawer calls into more useful ones."""

    # TODO: Complete
    @handler("irc cmd privmsg")
    def dispatch_privmsg(self, cmd, target_name, text):
        target = self.lookup_prefix(target_name)
        if self == target:
            pass # TODO Handle private queries.
        else:
            pass # TODO Handle public messages.

    @handler("irc cmd nick")
    def update_own_nick(self, cmd, new_nick):
        if self == cmd.source:
            self._nick = new_nick

    @handler("irc cmd ping")
    def reply_to_ping(self, cmd, *args):
        self.send_cmd(None, "PONG", args)
