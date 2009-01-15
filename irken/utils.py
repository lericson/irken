class AutoRegisterMixin(object):
    def connect(self, *args, **kwds):
        rv = super(AutoRegisterMixin, self).connect(*args, **kwds)
        user, real = self.autoregister
        self.send_cmd(None, "USER", (user, "*", "*", real))
        self.send_cmd(None, "NICK", (self.nick,))
        return rv
