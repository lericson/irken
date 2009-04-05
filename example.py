import logging
import irken

NICKNAME = "irken-nick"
USERNAME = "irken-user"
REALNAME = "irken realname"
ADDRNAME = "irc.lericson.se", 6667

logging.basicConfig(level=logging.DEBUG)

bot = irken.Connection(nick=NICKNAME, autoregister=(USERNAME, REALNAME))
bot.connect(ADDRNAME)
bot.run_forever()
