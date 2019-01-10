from Risque import Risque
from procedures import Verify
from ConfigurationDriver import ConfigurationDriver


class VerifyTicket:
    appUI = None

    def __init__(self, appUI):
        self.appUI = appUI

    def main(self):
        username = raw_input("Risque Username: ")
        password = raw_input("Risque Password (BoilerKey): ")
        ticketNumber = raw_input("Risque Ticket Number: ")
        print "Getting Info from Risque"
        risque = Risque(username, password)
        ticket = risque.getTicketData(ticketNumber)
        if ticket is None:
            print "Failed to get ticket from risque"
            self.appUI.goToMainPage()
            return
        self.__printDebugTicket(ticket)
        ConfigurationDriver.storeCredentials(username, password)
        Verify.Verify(ticket).run()

    def __printDebugTicket(self, ticket):
        print "PICS: {0}".format(len(ticket.pics))
        for pic in ticket.pics:
            print "\tPIC ID: {0}, Action: {1}, New Provider: {2}".format(pic.name, pic.action, pic.newProvider)
