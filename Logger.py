from COMMON import Common


class Logger:
    logFolder = None
    ticket = None
    sshLogFile = None
    generalLogFile = None

    def __init__(self, ticket):
        self.ticket = ticket
        self.logFolder = Common.getUserHome() + "larry/logs"

    def logSSH(self, string):
        raise NotImplementedError()

    def logWarning(self, string):
        raise NotImplementedError()

    def logError(self, string):
        raise NotImplementedError()

    def logInfo(self, string):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def getTimeStamp(self):
        raise NotImplementedError()
