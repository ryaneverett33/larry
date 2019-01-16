from Risque import Risque
from procedures import Config
from ConfigurationDriver import ConfigurationDriver


class ConfigTicket:
    appUI = None
    risque = None

    def __init__(self, appUI):
        self.appUI = appUI

    def main(self):
        username, risquePassword, switchPassword = ConfigurationDriver.getCredentials()
        ticketNumber = raw_input("Risque Ticket Number: ")
        print "Getting Info from Risque"
        if self.risque is None:
            self.risque = Risque(username, risquePassword)
        ticket = self.risque.getTicketData(ticketNumber)
        if ticket is None:
            print "Failed to get ticket from risque"
            self.appUI.goToMainPage()
            return
        self.__printDebugTicket(ticket)
        Config.Config(ticket).run()

    def __printDebugTicket(self, ticket):
        print "PICS: {0}".format(len(ticket.pics))
        for pic in ticket.pics:
            print "\tPIC ID: {0}, Action: {1}, New Provider: {2}".format(pic.name, pic.action, pic.newProvider)