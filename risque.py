import requests, lxml.html


class Risque:
    user = None
    password = None
    session = None

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.session = requests.session()

    def getTicketData(self, ticketNumber):
        raise NotImplementedError()
