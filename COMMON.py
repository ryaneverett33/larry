import re
import os


class Common:
    baseDir = "/home/ONEPURDUE/everettr/larry-release/"
    versionFile = "latest.version"
    userVersionFile = "larry.version"
    releaseFile = "latest.release"
    releasesDir = "releases/"
    executableFile = "larry"
    ignoreDirectories = [".git", ".idea", "risque-out"]

    @staticmethod
    def getLatestVersion():
        try:
            f = open(Common.baseDir + Common.versionFile, "r")
            version = f.readline()
            f.close()
            if len(version) == 0:
                return "0"
            return version
        except:
            return "0"

    # -1 if version2 > version1, 0 if equal, 1 if version1 > version 2
    @staticmethod
    def compareVersions(version1, version2):
        def normalize(v):
            return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

        return cmp(normalize(version1), normalize(version2))

    @staticmethod
    def getUserHome():
        username = os.getenv("USER")
        return "/home/ONEPURDUE/{0}/".format(username)
