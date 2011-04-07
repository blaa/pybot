#!/usr/bin/env /usr/bin/python

from __future__ import print_function

import sys

sys.path.append("..")

from frontends import Frontend, Jabber 

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:", sys.argv[0], "host user password")
        print("This testcase will try to connect and do something.")
        sys.exit(1)

    try:
        jabber = Jabber(sys.argv[1], sys.argv[2], sys.argv[3])
    except Frontend.FrontendException, e:
    	print(e)
