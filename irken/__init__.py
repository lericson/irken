class IRCError(Exception): pass
class UnhandledCommandError(IRCError): pass

from irken.base import Connection
from irken.dispatch import CommonDispatchMixin
from irken.encoding import EncodingMixin
from irken.io import SimpleSocketMixin
from irken.utils import AutoRegisterMixin

class Connection(AutoRegisterMixin, EncodingMixin, SimpleSocketMixin,
                 CommonDispatchMixin, Connection): pass

from logging import basicConfig as logging, DEBUG as LOG_DEBUG
