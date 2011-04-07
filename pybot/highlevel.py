#!/bin/env /usr/bin/python

# 0. Initialize some internals
# 1. Read defined commands, show any errors and quit if any
# 2. Determine which frontend to use (command line parameters?)
# 3. Initialize configured frontend, connect or die
# 4. Pass control to frontend (mainloop)

from __future__ import print_function

import sys

from frontends import Frontend 
from backends import MySQL, System
from commands import Commands
from log import Log

def run(config):
    # Do 0)
    log = Log.create(level=config.log_level, verbose=Log.NOTICE)

    sql = MySQL()
    system = System()

    # Do 1)
    try:
        commands = Commands(file=config.commands, sql=sql, system=system)
    except IOError, e:
        log.error("Unable to read commands file (check config)")
        log.error(e)
        sys.exit(1)

    # Do 2) and 3)
    try:
            if len(sys.argv) == 1:
                print("Give this script any command (try 'help') or --bot to start bot")
                sys.exit(2)
            elif len(sys.argv) == 2 and sys.argv[1] == "--bot":
                if config.jabber_enabled:
                    from frontends import Jabber
                    print("No arguments, starting bot")
                    frontend = Jabber(config.jabber_jid, 
                                      config.jabber_pass, commands)
                else:
                    # Workaround; importing modules takes a lots of time!
                    print("BOT MODE DISABLED; EDIT HIGHLEVEL.PY")
                    sys.exit(3)
            else:
                from frontends import CommandLine
                frontend = CommandLine(commands)
    except Frontend.FrontendException, e:
        print("Error while initializing frontend:", e)
        sys.exit(2)

    # Do 4)
    frontend.mainloop()

# vim:tabstop=4:expandtab
