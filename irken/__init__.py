class IRCError(Exception): pass
class UnhandledCommandError(IRCError): pass

from irken.base import BaseConnection
from irken.dispatch import CommonDispatchMixin
from irken.encoding import EncodingMixin
from irken.io import SimpleSocketMixin
from irken.utils import AutoRegisterMixin
from irken.ctcp import CTCPDispatchMixin

class Connection(CTCPDispatchMixin, AutoRegisterMixin, EncodingMixin,
                 SimpleSocketMixin, CommonDispatchMixin, BaseConnection): pass
    client_version = "irken"

from logging import basicConfig as logging, DEBUG as LOG_DEBUG
