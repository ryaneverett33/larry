from BufferedSsh import BufferedSsh
from shitSsh import shitSsh
from Ssh import Ssh
from PasswordUtility import PasswordUtility
import os
from COMMON import Common
import json


class ConfigurationDriver:
    user = None
    switchPassword = None
    risquePassword = None
    cookies = None
    loadedSession = None
    _lock = False

    @staticmethod
    def getDriver():
        return Ssh(ConfigurationDriver.user, ConfigurationDriver.switchPassword)

    @staticmethod
    def getCredentials():
        if not ConfigurationDriver.credentialsStored():
            userName = raw_input("Risque Username: ")
            risquepassword = PasswordUtility.getpassword("Risque Password (BoilerKey): ")
            switchpassword = PasswordUtility.getpassword("Switch Password: ")
            ConfigurationDriver.storeCredentials(userName, risquepassword, switchpassword)
        return ConfigurationDriver.user, ConfigurationDriver.risquePassword, ConfigurationDriver.switchPassword

    @staticmethod
    def storeCredentials(username, risquePassword, switchPassword):
        ConfigurationDriver.user = username
        ConfigurationDriver.switchPassword = switchPassword
        ConfigurationDriver.risquePassword = risquePassword

    @staticmethod
    def credentialsStored():
        return ConfigurationDriver.user is not None

    @staticmethod
    def storeCookies(cookies):
        try:
            keys = cookies.keys()
            ConfigurationDriver.cookies = dict()
            for key in keys:
                ConfigurationDriver.cookies[key] = cookies[key]
        except:
            ConfigurationDriver.cookies = None

    @staticmethod
    def cookiesStored():
        return ConfigurationDriver.cookies is not None

    @staticmethod
    def getCookies():
        return ConfigurationDriver.cookies

    @staticmethod
    def clearCookies():
        ConfigurationDriver.cookies = None

    @staticmethod
    def clearCredentials():
        ConfigurationDriver.user = None
        ConfigurationDriver.switchPassword = None
        ConfigurationDriver.risquePassword = None

    # Dirty hack for checking whether or not the user is still storing credentials when they hit ctrl-c
    # If they are, clear the credentials they stored because they probably made a mistake
    @staticmethod
    def lock():
        ConfigurationDriver._lock = True

    @staticmethod
    def unlock():
        ConfigurationDriver._lock = False

    @staticmethod
    def isLocked():
        return ConfigurationDriver._lock

    @staticmethod
    def useTestCredentials(username, switchPassword):
        ConfigurationDriver.user = username
        ConfigurationDriver.switchPassword = switchPassword

    @staticmethod
    def tryLoadSession():
        installDirectory = Common.getUserHome() + "larry/"
        sessionDirectory = installDirectory + Common.sessionDirectory
        if not os.path.exists(sessionDirectory):
            os.mkdir(sessionDirectory)
            return
        else:
            if os.path.exists(sessionDirectory + Common.sessionFile):
                # try and load the session
                try:
                    f = open(sessionDirectory + Common.sessionFile, "r")
                    data = f.read()
                    ConfigurationDriver.cookies = json.loads(data)
                    ConfigurationDriver.loadedSession = True
                    print "Loaded session: {0}".format(ConfigurationDriver.cookies)
                except Exception, e:
                    print "Failed to load session " + e

    @staticmethod
    def saveSession():
        installDirectory = Common.getUserHome() + "larry/"
        sessionDirectory = installDirectory + Common.sessionDirectory
        if not os.path.exists(sessionDirectory):
            os.mkdir(sessionDirectory)
        sessionData = json.dumps(ConfigurationDriver.cookies)
        f = open(sessionDirectory + Common.sessionFile, "w+")
        f.write(sessionData)
        f.close()

    @staticmethod
    def clearSession():
        ConfigurationDriver.cookies = None
        ConfigurationDriver.loadedSession = False
