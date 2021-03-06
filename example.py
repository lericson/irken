import os
import irken
from irken.dispatch import handler

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

def main(nick="irken-nick", username="irken-user", realname="irken realname",
         address=("irc.lericson.se", 6667), log_level=irken.LOG_DEBUG,
         cls=ExampleBot):
    irken.logging(level=log_level)
    bot = cls(nick=nick, autoregister=(username, realname))
    bot.connect(address)
    bot.run()

if __name__ == "__main__":
    main()
