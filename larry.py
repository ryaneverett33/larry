#!/usr/bin/python

from UI import UI
from PasswordUtility import PasswordUtility
import sys
from Hosts import Hosts
from INSTALL import Install


class larry:
    ui = None
    ignoreUpdate = False

    def __init__(self):
        self.ui = UI(self)
        self.parseArgs()
        if not self.ignoreUpdate:
            try:
                Install(lib=True).upgrade()
            except:
                return

    def run(self):
        self.ui.main()

    def parseArgs(self):
        for arg in sys.argv:
            if arg == "--editor" or arg == "-editor":
                PasswordUtility.useEditor()
            if arg == "--hostsDebug" or arg == "-hostsDebug":
                Hosts.USE_DEBUG = True
            if arg == "--ignoreUpdate" or arg == "-ignoreUpdate":
                self.ignoreUpdate = True
            if arg == "--disableArt" or arg == "-disableArt":
                self.ui.disableArt()


if __name__ == "__main__":
    app = larry()
    app.run()
