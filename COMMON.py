import re

class Common:
    baseDir = "/home/ONEPURDUE/everettr/larry-release/"
    versionFile = "latest.version"
    releaseFile = "latest.release"
    releasesDir = "releases/"

    @staticmethod
    def getLatestVersion():
        f = open(Common.baseDir + Common.versionFile)
        version = f.readline()
        f.close()
        return version

    # -1 if version2 > version1, 0 if equal, 1 if version1 > version 2
    @staticmethod
    def mycmp(version1, version2):
        def normalize(v):
            return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]

        return cmp(normalize(version1), normalize(version2))
