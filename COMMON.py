import re
import os
from datetime import datetime


class Common:
    baseDir = "/home/ONEPURDUE/everettr/larry-release/"
    versionFile = "latest.version"
    userVersionFile = "larry.version"
    releaseFile = "latest.release"
    releasesDir = "releases/"
    executableFile = "larry"
    sessionDirectory = "session/"
    sessionFile = "cookies.session"
    persistenceFile = "user.persistence"
    vrfList = "vrf.list"
    dataDirectory = "larry-data/"
    ignoreDirectories = [".git", ".idea", "risque-out"]
    changelogURL = "https://github.com/Changer098/larry/blob/master/CHANGELOG.md"
    __vrfHosts = None
    vrfDisabled = False
    VERSION = "0.48"

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

    @staticmethod
    def currentTimeString():
        # return datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        return datetime.now().strftime("%m-%d-%Y")

    @staticmethod
    def timeStringToDate(string):
        # return datetime.strptime(string, "%m-%d-%Y %H:%M:%S")
        return datetime.strptime(string, "%m-%d-%Y")

    @staticmethod
    def isHostVrfAffected(host):
        if Common.vrfDisabled:
            return False
        return host in Common.getVrfHosts()

    @staticmethod
    def getVrfHosts():
        if Common.vrfDisabled:
            return None
        if Common.__vrfHosts is None:
            hostList = open(Common.baseDir + Common.vrfList, "r")
            Common.__vrfHosts = hostList.readlines()
            for i in range(0, len(Common.__vrfHosts)):
                Common.__vrfHosts[i] = re.sub('[\r\n]', '', Common.__vrfHosts[i]).strip().encode('ascii', 'replace')
        return Common.__vrfHosts
