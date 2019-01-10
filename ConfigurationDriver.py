from BufferedSsh import BufferedSsh
from shitSsh import shitSsh
from Ssh import Ssh


class ConfigurationDriver:
    user = None
    password = None

    @staticmethod
    def getDriver():
        return Ssh(ConfigurationDriver.user, ConfigurationDriver.password)

    @staticmethod
    def storeCredentials(username, password):
        ConfigurationDriver.user = username
        ConfigurationDriver.password = password
