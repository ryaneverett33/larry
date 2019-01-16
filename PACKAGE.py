import sys
import os
from shutil import copyfile
from COMMON import Common


class Package:
    mode = None     # "new", "version"
    setVersion = False

    def __init__(self):
        self.parseArgs()

    def parseArgs(self):
        for arg in sys.argv:
            if arg == "-h" or arg == "--h":
                self.printHelp()
                sys.exit(1)
            elif arg == "-n" or arg == "--n":
                self.mode = "new"
            elif arg == "-s" or arg == "--s":
                self.setVersion = True
            elif arg == "-v" or arg == "--v":
                self.mode = "version"

    def backupPreviousRelease(self):
        previousReleaseLocation = Common.baseDir + Common.releaseFile
        newLocation = Common.baseDir + "previous.release"
        copyfile(previousReleaseLocation, newLocation)
        os.remove(previousReleaseLocation)

    def setCurrentRelease(self, releaseNumber):
        versionFile = Common.baseDir + Common.versionFile
        os.remove(versionFile)
        file = open(versionFile, "w")
        file.write(releaseNumber)
        file.close()

    def printHelp(self):
        print "larry - release helper HELP"
        print "-n\t--n\t\tCreate a new release"
        print "-s\t--s\t\tSet as latest version"
        print "-v\t--v\t\tGet the latest version"
        print "-h\t--h\t\tPrint this help screen"

    def createReleaseFile(self):

    def main(self):
        print "larry - release helper"
        if self.mode == "version":
            print "latest version: {0}".format(Common.getLatestVersion())
        elif self.mode == "new":
            directory = raw_input("directory: ")
            releaseNumber = None
            while releaseNumber is None:
                releaseNumber = raw_input("release number: ")
                try:
                    number = float(releaseNumber)
                except:
                    print "release number is invalid"
                    releaseNumber = None
            

        else:
            self.printHelp()

if __name__ == "__main__":
    Package().main()
