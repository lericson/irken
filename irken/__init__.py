class IRCError(Exception): pass
class UnhandledCommandError(IRCError): pass

from irken.base import BaseConnection
from irken.dispatch import CommonDispatchMixin
from irken.encoding import EncodingMixin
from irken.io import SelectIO
from irken.utils import AutoRegisterMixin, NicknameMixin
from irken.ctcp import CTCPDispatchMixin

class BaseMixin(object):
    client_version = "irken"
    make_io = SelectIO

bases = (BaseMixin, CTCPDispatchMixin, AutoRegisterMixin, EncodingMixin,
         CommonDispatchMixin, NicknameMixin, BaseConnection)

Connection = type("Connection", bases, {})

from logging import basicConfig as logging, DEBUG as LOG_DEBUG
