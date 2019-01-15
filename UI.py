from ui import VerifyTicket
from ConfigurationDriver import ConfigurationDriver


class UI:

    app = None
    pages = None
    currentPage = None
    exitApp = False

    def __init__(self, app):
        self.app = app
        self.pages = [
            ["Do Ticket", self.work_page],
            ["Verify Ticket", self.verify_page],
            ["Settings", self.settings_page],
            ["Store Credentials", self.credentials_page]
        ]
        self.goToMainPage()

    def main(self):
        while not self.exitApp:
            currentPage = self.currentPage
            currentPage[1]()

    def work_page(self):
        print "Work"
        self.goToMainPage()

    def verify_page(self):
        print "Verify"
        VerifyTicket.VerifyTicket(self).main()
        self.goToMainPage()

    def settings_page(self):
        print "Settings"
        self.goToMainPage()

    def credentials_page(self):
        print "Store Credentials"
        if ConfigurationDriver.credentialsStored():
            print "Credentials already stored"
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
                    print "invalid index: {0}, range: [0,{1}]".format(rawIndex, len(self.pages))
            except:
                print "Invalid Action, must be a value between 0 and {1}".format(len(self.pages) - 1)
        self.currentPage = self.pages[index]
        print "switching to page {0} with index {1}".format(self.currentPage[0], index)

    def goToMainPage(self):
        self.currentPage = ["Main Page", self.main_page]

    def __printPages(self):
        i = 0
        for page in self.pages:
            print "{0} - {1}".format(i, page[0])
            i = i + 1
