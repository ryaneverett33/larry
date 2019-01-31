#!/usr/bin/python

from UI import UI
from PasswordUtility import PasswordUtility
from ConfigurationDriver import ConfigurationDriver
import sys
from Hosts import Hosts
from INSTALL import Install
from Logger import Logger


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
        ConfigurationDriver.tryLoadSession()
        self.ui.main()

    def parseArgs(self):
        for arg in sys.argv:
            if arg == "--editor" or arg == "-editor":
                PasswordUtility.useEditor()
            elif arg == "--hostsDebug" or arg == "-hostsDebug":
                Hosts.USE_DEBUG = True
            elif arg == "--ignoreUpdate" or arg == "-ignoreUpdate":
                self.ignoreUpdate = True
            elif arg == "--disableArt" or arg == "-disableArt":
                self.ui.disableArt()
            elif arg == "--noLogging" or arg == "-noLogging":
                Logger.NO_LOGGING = True


if __name__ == "__main__":
    app = larry()
    app.run()
