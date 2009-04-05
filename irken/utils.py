class AutoRegisterMixin(object):
    def __init__(self, *args, **kwds):
        if "autoregister" in kwds:
            self.autoregister = kwds.pop("autoregister")
        super(AutoRegisterMixin, self).__init__(*args, **kwds)

    def connect(self, *args, **kwds):
        rv = super(AutoRegisterMixin, self).connect(*args, **kwds)
        user, real = self.autoregister
        self.send_cmd(None, "USER", (user, "*", "*", real))
        self.send_cmd(None, "NICK", (self.nick,))
        return rv
