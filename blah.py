import logging
from irken import Connection

logging.basicConfig(level=logging.DEBUG)

b = Connection(nick="toxik-bot", autoregister=("toxik-bot-u", "Toxik Bot R"))
b.connect(("irc.lericson.se", 6667))
b.run_forever()
