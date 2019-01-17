import sys
import os
from shutil import copyfile
from COMMON import Common
import zipfile
from os import walk
import signal


class Package:
    mode = None     # "new", "version"
    setVersion = False

    def __init__(self):
        self.parseArgs()
        signal.signal(signal.SIGINT, self.ctrlchandler)

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
        try:
            previousReleaseLocation = Common.baseDir + Common.releaseFile
            newLocation = Common.baseDir + "previous.release"
            copyfile(previousReleaseLocation, newLocation)
            os.remove(previousReleaseLocation)
        except:
            return

    def setCurrentRelease(self, releaseNumber):
        versionFile = Common.baseDir + Common.versionFile
        file = open(versionFile, "w")
        file.write(releaseNumber)
        file.close()

    def printHelp(self):
        print "larry - release helper HELP"
        print "-n\t--n\t\tCreate a new release"
        print "-s\t--s\t\tSet as latest version"
        print "-v\t--v\t\tGet the latest version"
        print "-h\t--h\t\tPrint this help screen"

    def getFiles(self, directory):
        f = []
        for (dirpath, dirnames, filenames) in walk(directory):
            cleaned = dirpath.split(directory)[1]
            if '\\' in cleaned:
                cleaned = cleaned.split('\\')[0]
            if '/' in cleaned:
                cleaned = cleaned.split('/')[0]
            if not cleaned in Common.ignoreDirectories:
                # f.extend(dirpath + '/' + filenames)
                for file in filenames:
                    if dirpath == directory:
                        f.append(file)
                    else:
                        f.append(dirpath + '/' + file)
        return f

    def createReleaseFile(self, filename, directory):
        files = self.getFiles(directory)
        if len(files) == 0:
            print "Empty directory, can't create release file"
            return False
        else:
            print "{0} files in directory, creating release file".format(len(files))
        with zipfile.ZipFile(filename, 'w') as myzip:
            # myzip.write('eggs.txt')
            i = 0
            for file in files:
                if i % 5 == 0:
                    print "{0}/{1}".format(i, len(files))
                myzip.write(file)
                i = i + 1
        return True

    def storeReleaseFile(self, filename):
        self.backupPreviousRelease()
        releaseFile = Common.baseDir + Common.releaseFile
        copyfile(filename, releaseFile)
        # Store in releases folder
        releasesFolder = Common.baseDir + Common.releasesDir + filename
        copyfile(filename, releasesFolder)

    def main(self):
        print "larry - release helper"
        if self.mode == "version":
            print "latest version: {0}".format(Common.getLatestVersion())
        elif self.mode == "new":
            directory = raw_input("directory: ")
            latestVersion = Common.getLatestVersion()
            releaseNumber = None
            while releaseNumber is None:
                releaseNumber = raw_input("release number: ")
                if self.setVersion and Common.compareVersions(releaseNumber, latestVersion) != 1:
                    print "release number not greater than current version {0}".format(latestVersion)
                    response = raw_input("do you want to set a different number (y/n)? ")
                    if response == "y":
                        releaseNumber = None
            # create release file
            filename = "{0}.release".format(releaseNumber)
            if self.createReleaseFile(filename, directory):
                print "Created release file at {0}".format(filename)
            else:
                print "Failed to create release file, quitting"
                return
            self.storeReleaseFile(filename)
            if self.setVersion:
                self.setCurrentRelease(releaseNumber)

        else:
            self.printHelp()

    def ctrlchandler(self, sig, frame):
        exit(0)


if __name__ == "__main__":
    Package().main()
