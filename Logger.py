from COMMON import Common
import time
import os
import traceback


class Logger:
    logFolder = None
    ticketNumber = None
    sshLogFile = None
    logFile = None
    ticketFolder = None
    instance = None
    NO_LOGGING = False

    # colors
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    NORMAL = "\033[0m"

    def __init__(self, ticketNumber, logFolder=None):
        self.ticketNumber = ticketNumber
        if not Logger.NO_LOGGING:
            if logFolder is None:
                self.logFolder = Common.getUserHome() + "larry/logs/"
            else:
                self.logFolder = logFolder
            self.ticketFolder = self.logFolder + str(ticketNumber) + "/"
            self.__createFolders()
            self.logFile = open(self.ticketFolder + "log.log", "a+")
            self.sshLogFile = open(self.ticketFolder + "ssh.log", "a+")
        Logger.instance = self

    def __createFolders(self):
        if not os.path.isdir(self.logFolder):
            os.mkdir(self.logFolder)
        if not os.path.isdir(self.ticketFolder):
            os.mkdir(self.ticketFolder)

    def logSSH(self, string):
        if Logger.NO_LOGGING:
            return
        self.sshLogFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.sshLogFile.flush()

    def logWarning(self, string, echo):
        if Logger.NO_LOGGING:
            if echo:
                self.printWarning(string)
            return
        self.logFile.write("|{0}| WARNING - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            # print self.WARNING + "WARNING " + string
            self.printWarning(string)

    def logError(self, string, echo):
        if Logger.NO_LOGGING:
            if echo:
                self.printError(string)
            return
        self.logFile.write("|{0}| ERROR - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            # print self.FAIL + "ERROR " + string
            self.printError(string)

    def logSuccess(self, string, echo):
        if Logger.NO_LOGGING:
            if echo:
                self.printSuccess(string)
            return
        self.logFile.write("|{0}| SUCCESS - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            self.printSuccess(string)

    def logException(self, string, exception, echo):
        if Logger.NO_LOGGING:
            if echo:
                self.printError(string)
            return
        self.logFile.write("|{0}| EXCEPTION - Message: {1}, Error: {2}\n".format(self.getTimeStamp(), exception, string))
        self.logFile.write(traceback.format_exc())
        self.logFile.flush()
        if echo:
            self.printError(string)

    def logInfo(self, string, echo):
        if Logger.NO_LOGGING:
            if echo:
                print string
            return
        self.logFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            print string

    @staticmethod
    def printWarning(string):
        print Logger.WARNING + string + Logger.NORMAL

    @staticmethod
    def printError(string):
        print Logger.FAIL + string + Logger.NORMAL

    @staticmethod
    def printSuccess(string):
        print Logger.OKGREEN + string + Logger.NORMAL

    @staticmethod
    def getInstance(ticketNumber):
        if ticketNumber is None:
            if Logger.instance is None:
                print Logger.FAIL + "Can't get singleton instance having not been initialized first" + Logger.NORMAL
                return None
            else:
                return Logger.instance
        else:
            if Logger.instance is None:
                return Logger(ticketNumber)
            else:
                if Logger.instance.ticketNumber != ticketNumber:
                    # overwrite
                    Logger.instance.close()
                    del Logger.instance
                    return Logger(ticketNumber)
                else:
                    return Logger.instance

    def close(self):
        self.logFile.close()
        self.sshLogFile.close()

    @staticmethod
    def getTimeStamp():
        localtime = time.localtime(time.time())
        pm = (False, True)[localtime.tm_hour > 11]
        minFixed = ("0{0}".format(localtime.tm_min), str(localtime.tm_min))[localtime.tm_min > 9]
        return "{0}:{1} {2}".format(localtime.tm_hour % 12, minFixed, ("AM", "PM")[pm])
