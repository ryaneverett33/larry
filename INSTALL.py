import sys
import os
from COMMON import Common

class Install:
    path = None

    def __init__(self):
        self.path = os.getenv("PATH")

    def addToPath(self, directory):
        os.putenv("PATH", self.path + ":" + directory)

    def main(self):
        print "Starting install for larry"


if __name__ == "__main__":
    install = Install()
    install.main()
