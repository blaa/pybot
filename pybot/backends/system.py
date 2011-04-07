import os

class System:
    def execute(self, cmd):
        pipe = os.popen(cmd, 'r')
        if not pipe:
            return None
        buf = pipe.read(5000)
        pipe.close()
        return buf

# vim:tabstop=4:expandtab
