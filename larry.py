from UI import UI
from PasswordUtility import PasswordUtility
import sys
from Hosts import Hosts


class larry:
    ui = None

    def __init__(self):
        self.parseArgs()
        self.ui = UI(self)

    def run(self):
        self.ui.main()

    def parseArgs(self):
        for arg in sys.argv:
            if arg == "--editor" or arg == "-editor":
                PasswordUtility.useEditor()
            if arg == "--hostsDebug" or arg == "-hostsDebug":
                Hosts.USE_DEBUG = True


if __name__ == "__main__":
    app = larry()
    app.run()
