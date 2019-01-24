from COMMON import Common
import time
import os


class Logger:
    logFolder = None
    ticket = None
    sshLogFile = None
    logFile = None
    ticketFolder = None

    #colors
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'

    def __init__(self, ticket, logFolder=None):
        self.ticket = ticket
        if logFolder is None:
            self.logFolder = Common.getUserHome() + "larry/logs/"
        else:
            self.logFolder = logFolder
        self.ticketFolder = self.logFolder + str(ticket) + "/"
        self.__createFolders()
        self.logFile = open(self.ticketFolder + "log.log", "w")
        self.sshLogFile = open(self.ticketFolder + "ssh.log", "w")

    def __createFolders(self):
        if not os.path.isdir(self.logFolder):
            os.mkdir(self.logFolder)
        if not os.path.isdir(self.ticketFolder):
            os.mkdir(self.ticketFolder)

    def logSSH(self, string):
        self.sshLogFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.sshLogFile.flush()

    def logWarning(self, string, echo):
        self.logFile.write("|{0}| WARNING - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            print self.WARNING + "WARNING " + string

    def logError(self, string, echo):
        self.logFile.write("|{0}| ERROR - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            print self.FAIL + "ERROR " + string

    def logInfo(self, string, echo):
        self.logFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            print string

    @staticmethod
    def printWarning(string):
        print Logger.WARNING + string

    @staticmethod
    def printError(string):
        print Logger.FAIL + string

    @staticmethod
    def printSuccess(string):
        print Logger.OKGREEN + string

    def close(self):
        self.logFile.close()
        self.sshLogFile.close()

    @staticmethod
    def getTimeStamp():
        localtime = time.localtime(time.time())
        pm = (False, True)[localtime.tm_hour > 11]
        minFixed = ("0{0}".format(localtime.tm_min), str(localtime.tm_min))[localtime.tm_min > 9]
        return "{0}:{1} {2}".format(localtime.tm_hour % 12, minFixed, ("AM", "PM")[pm])
