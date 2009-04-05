import os
import irken
from irken.dispatch import handler

NICKNAME = "irken-nick"
USERNAME = "irken-user"
REALNAME = "irken realname"
ADDRNAME = "irc.lericson.se", 6667

class ExampleBot(irken.Connection):
    @property
    def client_version(self):
        reffn = ".git/refs/heads/master"
        rv = "irken example bot"
        if os.path.exists(reffn):
            rev = open(reffn, "U").read().rstrip("\n")
            return rv + " (master is %s)" % rev
        else:
            return rv

    def make_source(self, prefix):
        source = super(ExampleBot, self).make_source(prefix)
        source.msg_counts = {}
        return source

    @handler("irc cmd privmsg")
    def count_message_direction(self, cmd, target_name, text):
        src = cmd.source
        target = self.lookup_prefix((target_name,))
        count = src.msg_counts.get(target, -1)
        count = src.msg_counts[target] = count + 1
        if self == target:
            print "%04d *** <%s> %s" % (count, src.nick, text)
        else:
            print "%04d <%s:%s> %s" % (count, src.nick, target.nick, text)

irken.logging(level=irken.LOG_DEBUG)
bot = ExampleBot(nick=NICKNAME, autoregister=(USERNAME, REALNAME))
#bot.connect(ADDRNAME)
bot.consume(":toxik PRIVMSG " + bot.nick + " :\x01VERSION\x01\n")
#bot.run_forever()
