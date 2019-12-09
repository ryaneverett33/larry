from simplecrypt import encrypt, decrypt
from COMMON import Common
from ConfigurationDriver import ConfigurationDriver
from Risque import Risque
import base64
import json
import hashlib
import os
import datetime
import random


class PersistenceModule:
    persistenceFile = None
    instance = None
    KEY_LENGTH = 16
    DISABLED = False

    def __init__(self):
        if self.DISABLED:
            return
        self.persistenceFile = Common.getUserHome() + Common.dataDirectory + Common.persistenceFile
        if os.path.exists(self.persistenceFile):
            # try and load session info
            try:
                key = self.__createKey()
                cipherData = open(self.persistenceFile, 'r').read()
                plainData = self.decrypt(cipherData, key)
                # get json data
                data = json.loads(plainData)
                # check expire date
                if self.__isExpired(data["expire"]):
                    os.remove(self.persistenceFile)
                    print("Persistence File expired")
                else:
                    # load credentials and cookies
                    ConfigurationDriver.storeCredentials(data["credentials"]["username"], data["credentials"]["risquePassword"],
                                                         data["credentials"]["switchPassword"])
                    ConfigurationDriver.storeCookies(data["cookies"])
                    # test
                    username, risquePassword, password = ConfigurationDriver.getCredentials()
                    risque = Risque(username, risquePassword)
                    if not risque.testSession():
                        # session is invalid
                        print("Persistence Module loaded an invalid session")
                        # clean up
                        ConfigurationDriver.clearCookies()
                        ConfigurationDriver.clearCredentials()
                        ConfigurationDriver.loadedSession = False
                        os.remove(self.persistenceFile)
                    else:
                        # session is valid
                        print("Persistence Module loaded a valid session")
                        ConfigurationDriver.loadedSession = True
            except Exception as e:
                # failed to read data, erase it
                os.remove(self.persistenceFile)
                self.loaded = False
        PersistenceModule.instance = self

    # Return base64 encoded ciphertext
    def encrypt(self, plaintext, key):
        ciphertext = encrypt(key, plaintext)
        return base64.b64encode(ciphertext)

    # Return base64 decoded plaintext
    def decrypt(self, ciphertext, key):
        nonb64 = base64.b64decode(ciphertext)
        return decrypt(key, nonb64)

    # Saves a new valid session
    def save(self):
        if self.DISABLED:
            return
        try :
            username, risquePassword, password = ConfigurationDriver.getCredentials()
            data = {
                "expire": self.__getExpireDate(),
                "credentials": {
                    "username": username,
                    "risquePassword": risquePassword,
                    "switchPassword": password
                },
                "cookies": ConfigurationDriver.getCookies()
            }
            jsonStr = json.dumps(data)
            key = self.__createKey()
            ciphertext = self.encrypt(jsonStr, key)
            if not os.path.isdir(Common.getUserHome() + Common.dataDirectory):
                os.mkdir(Common.getUserHome() + Common.dataDirectory)
            f = open(self.persistenceFile, "w+")
            f.write(ciphertext)
            ConfigurationDriver.loadedSession = True
        except Exception as e:
            print("Failed to save Session, error {0}".format(e))

    # Create encryption/decryption key
    def __createKey(self):
        username = os.getenv("USER")
        time = datetime.datetime.now().strftime("%m-%d-%Y")
        m = hashlib.sha256()
        m.update(username)
        m.update(time)
        seed = m.hexdigest()
        random.seed(seed)
        key = ""
        for i in range(0, self.KEY_LENGTH):
            # range [32,127]
            key = key + chr(random.randint(32, 127))
        return key

    # Check if session is expired
    def __isExpired(self, date):
        dateObj = Common.timeStringToDate(date)
        return dateObj.day < datetime.datetime.now().day

    # Get new expiration date
    def __getExpireDate(self):
        now = datetime.datetime.now()
        now = now.replace(day=now.day + 1)
        return now.strftime("%m-%d-%Y")

    @staticmethod
    def getInstance(noInit=False):
        if PersistenceModule.instance is None and not noInit:
            return PersistenceModule()
        elif PersistenceModule.instance is None and noInit:
            return None
        return PersistenceModule.instance
