import unittest
from Risque import Risque


class ParsingTests(unittest.TestCase):
    @classmethod
    def getTicketBody(cls, filelocation):
        f = open(filelocation, 'r')
        return f.read()

    def test_parseModify(self):
        ticketBody = self.getTicketBody('../risque-out/67159.html')
        self.assertIsNotNone(ticketBody, "Failed to read ticket, setUp failed")
        r = Risque('u', 'p')
        ticket = r.parseTicket(ticketBody)
        self.assertIsNotNone(ticket)

    def test_parseActivate(self):
        ticketBody = self.getTicketBody('../risque-out/67118.html')
        self.assertIsNotNone(ticketBody, "Failed to read ticket, setUp failed")
        r = Risque('u', 'p')
        ticket = r.parseTicket(ticketBody)
        self.assertIsNotNone(ticket)

    def test_bigModify(self):
        ticketBody = self.getTicketBody('../risque-out/67160.html')
        self.assertIsNotNone(ticketBody, "Failed to read ticket, setUp failed")
        r = Risque('u', 'p')
        ticket = r.parseTicket(ticketBody)
        self.assertIsNotNone(ticket)

    def test_deactivate(self):
        ticketBody = self.getTicketBody('../risque-out/67154.html')
        self.assertIsNotNone(ticketBody, "Failed to read ticket, setUp failed")
        r = Risque('u', 'p')
        ticket = r.parseTicket(ticketBody)
        self.assertIsNotNone(ticket)