from Risque import Risque
from procedures import Verify
from ConfigurationDriver import ConfigurationDriver


class VerifyTicket:
    appUI = None
    risque = None

    def __init__(self, appUI):
        self.appUI = appUI

    def main(self, ticketNumber=None):
        if not ConfigurationDriver.credentialsStored():
            ConfigurationDriver.lock()
        username, risquePassword, switchPassword = ConfigurationDriver.getCredentials()
        if ticketNumber is None:
            ticketNumber = raw_input("Risque Ticket Number: ")
        ConfigurationDriver.unlock()
        print "Getting Info from Risque"
        if self.risque is None:
            self.risque = Risque(username, risquePassword)
        ticket = self.risque.getTicketData(ticketNumber)
        if ticket is None:
            print "Failed to get ticket from risque"
            if self.appUI is not None:
                self.appUI.goToMainPage()
            return
        self.__printDebugTicket(ticket)
        Verify.Verify(ticket).run()

    def __printDebugTicket(self, ticket):
        print "PIC count: {0}, configurable PIC count: {1}".format(len(ticket.pics), len(ticket.configurablePics))
        for pic in ticket.configurablePics:
            print "\tPIC ID: {0}, Action: {1}, New Provider: {2}".format(pic.name, pic.action, pic.newProvider)
