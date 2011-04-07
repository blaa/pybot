import sys
from frontend import Frontend

class CommandLine(Frontend):
    def __init__(self, commands):
        # Command parsing / executing interface
        self.commands = commands

    def mainloop(self):
        assert len(sys.argv) > 1
        sur = ['"' + s + '"' for s in sys.argv[1:]]
        cmd = " ".join(sur)
        reply = self.commands.execute_command(cmd, "local")
        print reply
        return reply

# vim:tabstop=4:expandtab
