import irken
from irken.dispatch import handler

NICKNAME = "irken-nick"
USERNAME = "irken-user"
REALNAME = "irken realname"
ADDRNAME = "irc.lericson.se", 6667

class ExampleBot(irken.Connection):
    def make_source(self, prefix):
        source = super(ExampleBot, self).make_source(prefix)
        source.msg_counts = {}
        return source

    @handler("privmsg")
    def count_message_direction(self, cmd, target_name, text):
        src = cmd.source
        target = self.lookup_prefix(target_name)
        count = src.msg_counts.get(target, -1)
        src.msg_counts[target] = count = count + 1
        if self == target:
            print "%04d *** <%s> %s" % (count, src.nick, text)
        else:
            print "%04d <%s:%s> %s" % (count, src.nick, target.nick, text)

irken.logging(level=irken.LOG_DEBUG)
bot = ExampleBot(nick=NICKNAME, autoregister=(USERNAME, REALNAME))
bot.connect(ADDRNAME)
bot.run_forever()
