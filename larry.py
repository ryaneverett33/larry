#!/usr/bin/python

from UI import UI
from PasswordUtility import PasswordUtility
from PersistenceModule import PersistenceModule
import sys
from Hosts import Hosts
from INSTALL import Install
from Logger import Logger
from COMMON import Common
from ui import ConfigTicket
from ui import VerifyTicket


class larry:
    ui = None
    ignoreUpdate = False
    disablePersistence = False
    doTicket = None
    verifyTicket = None

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
        if self.doTicket is not None:
            return ConfigTicket.ConfigTicket(None).main(self.doTicket)
        elif self.verifyTicket is not None:
            return VerifyTicket.VerifyTicket(None).main(self.verifyTicket)
        self.ui.main()

    def __showHelp(self):
        print("usage: larry [option]")
        print("  -t, --t NUM\t\t\t\tDo a ticket and exit")
        print("  -v, --v NUM\t\t\t\tVerify a ticket and exit")
        print("")
        print("  -editor, --editor\t\t\t[DEBUG]Force password utility to act as if it's in an editor")
        print("  -hostsDebug, --hostsDebug\t\t[DEBUG]Force larry to use the debug version of the hosts file")
        print("  -ignoreUpdate, --ignoreUpdate\t\tDisallow larry to check for updates on launch")
        print("  -disableArt, --disableArt\t\tDoesn't print larry the lobster art :(")
        print("  -noLogging, --noLogging\t\tTurns off debug logging")
        print("  -disableVrf, --disableVrf\t\tDisables larry's VRF workaround")
        print("  -disableColor, --disableColor\t\tDisable color output")
        print("  -disablePM, --disablePM\t\tDisables the Persistence Module")
        print("  -h, --h\t\t\t\tDisplays this help screen")
        print("  -V, --V\t\t\t\tDisplays the current version")

    def __invalidTicketFormat(self, arg):
        print("Invalid Ticket Number")
        print("USAGE: larry {0} NUMBER, e.g. larry {0} 69420".format(arg))
        exit(-1)

    def __printVersion(self):
        print("larry version {0}".format(Common.VERSION))

    def parseArgs(self):
        for i in range(0, len(sys.argv)):
            arg = sys.argv[i]
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
            elif arg == "-t" or arg == "--t":
                if i + 1 >= len(sys.argv):
                    self.__invalidTicketFormat(arg)
                else:
                    self.doTicket = sys.argv[i + 1]
                    try:
                        int(self.doTicket)
                    except Exception:
                        self.__invalidTicketFormat(arg)
                    i = i + 1
            elif arg == "-v" or arg == "--v":
                if i + 1 >= len(sys.argv):
                    self.__invalidTicketFormat(arg)
                else:
                    self.verifyTicket = sys.argv[i + 1]
                    try:
                        int(self.verifyTicket)
                    except Exception:
                        self.__invalidTicketFormat(arg)
                    i = i + 1
            elif arg == "--h" or arg == "-h":
                self.__showHelp()
                exit(1)
            elif arg == "--V" or arg == "-V":
                self.__printVersion()


if __name__ == "__main__":
    app = larry()
    app.run()
