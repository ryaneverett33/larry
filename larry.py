#!/usr/bin/python

from UI import UI
from PasswordUtility import PasswordUtility
from PersistenceModule import PersistenceModule
import sys
from Hosts import Hosts
from INSTALL import Install
from Logger import Logger
from COMMON import Common


class larry:
    ui = None
    ignoreUpdate = False
    disablePersistence = False

    def __init__(self):
        self.ui = UI(self)
        self.parseArgs()
        if not self.ignoreUpdate:
            try:
                Install(lib=True).upgrade()
            except:
                return

    def run(self):
        if not self.disablePersistence:
            PersistenceModule.getInstance()
        else:
            PersistenceModule.DISABLED = True
        self.ui.main()

    def showHelp(self):
        print "usage: larry [option]"
        print "  -editor, --editor\t\t\t[DEBUG]Force password utility to act as if it's in an editor"
        print "  -hostsDebug, --hostsDebug\t\t[DEBUG]Force larry to use the debug version of the hosts file"
        print "  -ignoreUpdate, --ignoreUpdate\t\tDisallow larry to check for updates on launch"
        print "  -disableArt, --disableArt\t\tDoesn't print larry the lobster art :("
        print "  -noLogging, --noLogging\t\tTurns off debug logging"
        print "  -disableVrf, --disableVrf\t\tDisables larry's VRF workaround"
        print "  -disableColor, --disableColor\t\tDisable color output"
        print "  -disablePM, --disablePM\t\tDisables the Persistence Module"
        print "  -h, --h\t\t\t\tDisplays this help screen"

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
                Logger.StdoutLogger()
            elif arg == "--disableVrf" or arg == "-disableVrf":
                Common.vrfDisabled = True
            elif arg == "--disableColor" or arg == "-disableColor":
                Logger.disableColor = True
            elif arg == "--disablePM" or arg == "-disablePM":
                self.disablePersistence = True
            elif arg == "--h" or arg == "-h":
                self.showHelp()
                exit(1)


if __name__ == "__main__":
    app = larry()
    app.run()
