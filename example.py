class MyIRCBot(irken.Connection):
    def on_joined(self, who, where):
        if who is self:
            print "I joined", where
        else:
            print who, "joined", where

    def on_message(self, sender, receiver, text):
        if receiver is self:
            logger.debug("Private message: %s", text)
        print "<%s:%s> %s" % (sender.nickname, receiver, text)

# Method 1: plain setting the socket attr.
b = MyIRCBot(nick="toxik-bot", autoregister=("toxik-bot-u", "Toxik Bot R"))
b.socket = a_socket
b.run_forever()

# Method 2: creating with a utility method.
b = MyIRCBot.make_connected(address=("irc.lericson.se", 6667), nick="toxik-bot",
                            autoregister=("toxik-bot-u", "Toxik Bot R"))
b.run_forever()

# Method 3: using a connector.
def spawner(connector):
    print "Connection attempt #%d" % (connector.attempts + 1,)
    return MyIRCBot(nick="toxik-bot", autoregister=("toxik-bot-u", "Toxik Bot R"))
conntor = Connector(spawner=spawner, address=("irc.lericson.se", 6667))
conntor.run_forever()
