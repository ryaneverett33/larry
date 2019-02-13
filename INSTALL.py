import os
import os.path
from COMMON import Common
import zipfile
import shutil
import stat
import signal


class Install:
    path = None

    def __init__(self, lib=False):
        self.path = os.getenv("PATH")
        if not lib:
            signal.signal(signal.SIGINT, self.ctrlchandler)

    def isAlreadyInstalled(self, directory):
        return os.path.isfile(directory + Common.userVersionFile)

    def getInstalledVersion(self, directory):
        try:
            f = open(directory + Common.userVersionFile, "r")
            version = f.readline()
            f.close()
            if len(version) == 0:
                return "0"
            return version
        except:
            return "0"

    def isUpgradeAvailable(self):
        installedVersion = self.getInstalledVersion(Common.getUserHome() + "larry/")
        return Common.compareVersions(installedVersion, Common.getLatestVersion()) == -1

    def upgrade(self, installDirectory=None, force=False):
        installFile = Common.baseDir + Common.releaseFile
        if installDirectory is None:
            installDirectory = Common.getUserHome() + "larry/"
        if not force:
            if self.isAlreadyInstalled(installDirectory):
                if not self.isUpgradeAvailable():
                    return
        # Remove what's currently installed
        shutil.rmtree(installDirectory)
        zipfile.ZipFile(installFile).extractall(installDirectory)
        self.makeExecutable(installDirectory + Common.executableFile)
        self.addToPath()
        self.writeVersion(Common.getLatestVersion(), installDirectory)
        print "Changelog at {0}".format(Common.changelogURL)
        print "Upgraded larry to version {0}".format(Common.getLatestVersion())

    def makeExecutable(self, file):
        # https://stackoverflow.com/a/12792002
        st = os.stat(file)
        os.chmod(file, st.st_mode | stat.S_IEXEC)

    def writeVersion(self, version, installDirectory):
        f = open(installDirectory + Common.userVersionFile, "w")
        f.write(version)
        f.close()

    def inPath(self):
        try:
            bashrc = open("{0}/.bashrc".format(Common.getUserHome()), "r")
            lines = bashrc.read()
            path = os.getenv("PATH")
            return "larry" in path or "### larry" in lines
        except:
            return False

    def addToPath(self):
        if self.inPath():
            return
        # add to ~/.bashrc & ~/.profile
        command = "export PATH=$PATH:/home/ONEPURDUE/${USER}/larry"
        comment = "### larry"
        bashrc = open("{0}/.bashrc".format(Common.getUserHome()), "a+")
        profile = open("{0}/.profile".format(Common.getUserHome()), "a+")
        bashrc.write("\n\n{0}\n{1}\n".format(comment, command))
        profile.write("\n\n{0}\n{1}\n".format(comment, command))
        bashrc.close()
        profile.close()

    def main(self):
        print "Starting install for larry"
        installDirectory = Common.getUserHome() + "larry/"
        if self.isAlreadyInstalled(installDirectory):
            if self.isUpgradeAvailable():
                response = raw_input("larry is already installed, but out-of-date. Do you want to update? (y/n)")
                if response == "n" or response == "N":
                    exit(-1)
                self.upgrade(installDirectory, force=True)
        else:
            installFile = Common.baseDir + Common.releaseFile
            print "Installing at {0}".format(installDirectory)
            zipfile.ZipFile(installFile).extractall(installDirectory)
            self.makeExecutable(installDirectory + Common.executableFile)
            self.addToPath()
            self.writeVersion(Common.getLatestVersion(), installDirectory)
            print "Changelog at {0}".format(Common.changelogURL)
            print "Installed larry version {0}".format(Common.getLatestVersion())

    def ctrlchandler(self, sig, frame):
        exit(0)


if __name__ == "__main__":
    install = Install()
    install.main()
