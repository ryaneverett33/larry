from ui import VerifyTicket
from ui import ConfigTicket
from ConfigurationDriver import ConfigurationDriver
import signal
from ui import art
from paramiko import AuthenticationException
from PasswordUtility import PasswordUtility
import traceback


class UI:
    app = None
    pages = None
    currentPage = None
    exitApp = False
    artDisabled = False

    def __init__(self, app):
        self.app = app
        self.pages = [
            ["Do Ticket", self.work_page],
            ["Verify Ticket", self.verify_page],
            ["Store Credentials", self.credentials_page],
            ["Exit", self.exit],
            ["Art", self.artPage]
        ]
        self.goToMainPage()
        signal.signal(signal.SIGINT, self.ctrlchandler)

    def main(self):
        if not self.artDisabled:
            print(art.art.getArt())
        while not self.exitApp:
            currentPage = self.currentPage
            try:
                currentPage[1]()
            except AuthenticationException:
                result = raw_input("Failed to login to switch, change switch password? (y/n)")
                if result.lower() == "y":
                    newPassword = PasswordUtility.getpassword("Switch Password: ")
                    user, risquePass, switchPass = ConfigurationDriver.getCredentials()
                    ConfigurationDriver.storeCredentials(user, risquePass, newPassword)
                self.goToMainPage()
            except StopIteration:
                self.goToMainPage()
            except Exception as e:
                print(e)
                print(traceback.format_exc())
                self.goToMainPage()

    def work_page(self):
        print("Work")
        ConfigTicket.ConfigTicket(self).main()
        self.goToMainPage()

    def verify_page(self):
        print("Verify")
        VerifyTicket.VerifyTicket(self).main()
        self.goToMainPage()

    def settings_page(self):
        print("Settings")
        self.goToMainPage()

    def credentials_page(self):
        print("Store Credentials")
        if ConfigurationDriver.credentialsStored():
            print("Credentials already stored")
            response = raw_input("overwrite? (y/n): ")
            if response.lower() == "y":
                ConfigurationDriver.getCredentials()
        else:
            ConfigurationDriver.getCredentials()
        self.goToMainPage()

    def main_page(self):
        self.__printPages()
        index = -1
        while index < 0 or index >= len(self.pages):
            rawIndex = raw_input("Choose Action: ")
            try:
                rawIndex = int(rawIndex)
                if rawIndex >= 0 and rawIndex < len(self.pages):
                    index = rawIndex
                    break
                else:
                    print("invalid index: {0}, range: [0,{1}]".format(rawIndex, len(self.pages)))
            except:
                print("Invalid Action, must be a value between 0 and {0}".format(len(self.pages) - 1))
        self.currentPage = self.pages[index]
        # print("switching to page {0} with index {1}".format(self.currentPage[0], index)

    def exit(self):
        self.exitApp = True

    def goToMainPage(self):
        self.currentPage = ["Main Page", self.main_page]

    def artPage(self):
        print(art.art.getArt())
        self.goToMainPage()

    # The saddest setting
    def disableArt(self):
        self.artDisabled = True
        self.pages.remove(["Art", self.artPage])

    def __printPages(self):
        i = 0
        for page in self.pages:
            print("{0} - {1}".format(i, page[0]))
            i = i + 1

    def ctrlchandler(self, sig, frame):
        if ConfigurationDriver.isLocked():
            ConfigurationDriver.clearCredentials()
            ConfigurationDriver.unlock()
        if self.currentPage[0] == "Main Page":
            self.exit()
        # raise an exception on main thread, and leave
        raise StopIteration()
