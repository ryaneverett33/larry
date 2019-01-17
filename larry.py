from UI import UI
from PasswordUtility import PasswordUtility
import sys
from Hosts import Hosts
from INSTALL import Install


class larry:
    ui = None
    ignoreUpdate = False

    def __init__(self):
        self.parseArgs()
        self.ui = UI(self)
        if not self.ignoreUpdate:
            Install(lib=True).upgrade()

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


if __name__ == "__main__":
    app = larry()
    app.run()
