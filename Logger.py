from COMMON import Common
import time
import os
import traceback
import sys
import datetime


class Logger:
    logFolder = None
    ticketNumber = None
    sshLogFile = None
    beforeAfterFile = None
    logFile = None
    ticketFolder = None
    instance = None
    disableColor = False
    beforeAfterConfigs = dict() # dict(picName) -> [beforeConfig, afterConfig]

    # colors
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKGREEN = '\033[92m'
    HEADER = '\033[95m'
    NORMAL = "\033[0m"

    def __init__(self, ticketNumber, logFolder=None, noLogging=False):
        self.ticketNumber = ticketNumber
        if noLogging:
            self.logFile = sys.stdout
            self.sshLogFile = sys.stdout
            self.beforeAfterFile = sys.stdout
        else:
            if logFolder is None:
                self.logFolder = Common.getUserHome() + Common.dataDirectory + "logs/"
            else:
                self.logFolder = logFolder
            self.ticketFolder = self.logFolder + str(ticketNumber) + "/"
            self.__createFolders()
            self.logFile = open(self.ticketFolder + "log.log", "a+")
            self.sshLogFile = open(self.ticketFolder + "ssh.log", "a+")
            self.beforeAfterFile = open(self.ticketFolder + "beforeAfter.log", "a+")
            self.__writeHeaders()
        Logger.instance = self

    def __createFolders(self):
        if not os.path.isdir(Common.getUserHome() + Common.dataDirectory):
            os.mkdir(Common.getUserHome() + Common.dataDirectory)
        if not os.path.isdir(self.logFolder):
            os.mkdir(self.logFolder)
        if not os.path.isdir(self.ticketFolder):
            os.mkdir(self.ticketFolder)

    def __writeHeaders(self):
        if self.logFile is not sys.stdout:
            # write Log File Headers
            self.logFile.writelines(
                ["#### larry|Log ####\n", "# {0} #\n".format(Logger.getTimeStamp()), "###################\n"])
            self.sshLogFile.writelines(
                ["#### larry|SSH Log ####\n", "# {0} #\n".format(Logger.getTimeStamp()), "###################\n"])
            self.beforeAfterFile.writelines(
                ["#### larry|Before And After ####\n", "# {0} #\n".format(Logger.getTimeStamp()), "###################\n"])

    def logSSH(self, string):
        self.sshLogFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.sshLogFile.flush()

    def logWarning(self, string, echo):
        self.logFile.write("|{0}| WARNING - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            # print self.WARNING + "WARNING " + string
            self.printWarning(string)

    def logError(self, string, echo):
        self.logFile.write("|{0}| ERROR - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            # print self.FAIL + "ERROR " + string
            self.printError(string)

    def logBefore(self, picName, interface, config):
        if picName not in self.beforeAfterConfigs:
            self.beforeAfterConfigs[picName] = [None, None]
        if self.beforeAfterConfigs[picName] is None:
            return
        self.beforeAfterConfigs[picName][0] = config
        if self.beforeAfterConfigs[picName][0] is not None and self.beforeAfterConfigs[picName][1] is not None:
            # write out the configs
            self.beforeAfterFile.write("\t {1}:{0} Before\n".format(picName, interface))
            #
            # This is I/O bottle-necked. A bulk write() would be more efficient, or writelines(). writelines() doesn't
            # append new lines though.
            #
            for line in self.beforeAfterConfigs[picName][0]:
                self.beforeAfterFile.write(line + '\n')
            self.beforeAfterFile.write("\t {1}:{0} After\n".format(picName, interface))
            for line in self.beforeAfterConfigs[picName][1]:
                self.beforeAfterFile.write(line + '\n')
            self.beforeAfterConfigs[picName] = None
            self.beforeAfterFile.flush()

    def logAfter(self, picName, interface, config):
        if picName not in self.beforeAfterConfigs:
            self.beforeAfterConfigs[picName] = [None, None]
        if self.beforeAfterConfigs[picName] is None:
            return
        self.beforeAfterConfigs[picName][1] = config
        if self.beforeAfterConfigs[picName][0] is not None and self.beforeAfterConfigs[picName][1] is not None:
            # write out the configs
            self.beforeAfterFile.write("\t {0}-{1} Before\n".format(picName, interface))
            #
            # This is I/O bottle-necked. A bulk write() would be more efficient, or writelines(). writelines() doesn't
            # append new lines though.
            #
            for line in self.beforeAfterConfigs[picName][0]:
                self.beforeAfterFile.write(line + '\n')
            self.beforeAfterFile.write("\t {0}-{1} After\n".format(picName, interface))
            for line in self.beforeAfterConfigs[picName][1]:
                self.beforeAfterFile.write(line + '\n')
            self.beforeAfterConfigs[picName] = None
            self.beforeAfterFile.flush()

    def logSuccess(self, string, echo):
        self.logFile.write("|{0}| SUCCESS - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            self.printSuccess(string)

    def logException(self, string, exception, echo):
        self.logFile.write("|{0}| EXCEPTION - Message: {1}, Error: {2}\n".format(self.getTimeStamp(), exception, string))
        self.logFile.write(traceback.format_exc())
        self.logFile.flush()
        if echo:
            self.printError(string)

    def logInfo(self, string, echo):
        self.logFile.write("|{0}| - {1}\n".format(self.getTimeStamp(), string))
        self.logFile.flush()
        if echo:
            print string

    @staticmethod
    def printWarning(string):
        if Logger.disableColor:
            print Logger.NORMAL + string + Logger.NORMAL
        else:
            print Logger.WARNING + string + Logger.NORMAL

    @staticmethod
    def printError(string):
        if Logger.disableColor:
            print Logger.NORMAL + string + Logger.NORMAL
        else:
            print Logger.FAIL + string + Logger.NORMAL

    @staticmethod
    def printSuccess(string):
        if Logger.disableColor:
            print Logger.NORMAL + string + Logger.NORMAL
        else:
            print Logger.OKGREEN + string + Logger.NORMAL

    @staticmethod
    def getInstance(ticketNumber):
        if ticketNumber is None:
            if Logger.instance is None:
                print Logger.FAIL + "Can't get singleton instance having not been initialized first" + Logger.NORMAL
                return Logger.StdoutLogger()
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
        if self.logFile is not sys.stdout:
            self.logFile.close()
            self.sshLogFile.close()
            self.beforeAfterFile.close()

    @staticmethod
    def getTimeStamp():
        localtime = time.localtime(time.time())
        # pm = (False, True)[localtime.tm_hour > 11]
        pm = True if localtime.tm_hour > 11 else False
        hourFixed = localtime.tm_hour % 12 if localtime.tm_hour != 12 else 12
        minFixed = ("0{0}".format(localtime.tm_min), str(localtime.tm_min))[localtime.tm_min > 9]
        return "{0}:{1} {2}".format(hourFixed, minFixed, ("AM", "PM")[pm])

    @staticmethod
    def StdoutLogger():
        return Logger(-1, noLogging=True)
