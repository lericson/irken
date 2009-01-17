import logging
from irken.base import Connection
from irken.dispatch import CommonDispatchMixin
from irken.encoding import EncodingMixin
from irken.io import SimpleSocketMixin
from irken.utils import AutoRegisterMixin

logging.basicConfig(level=logging.DEBUG)

class Blah(AutoRegisterMixin, EncodingMixin, SimpleSocketMixin,
           CommonDispatchMixin, Connection): pass

b = Blah(nick="toxik-bot")
b.autoregister = "toxik-bot-u", "Toxik Bot R"
b.connect(("irc.lericson.se", 6667))
b.run_forever()
