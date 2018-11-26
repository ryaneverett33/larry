import requests, lxml.html
import re
from bs4 import BeautifulSoup, NavigableString
from Ticket import Ticket
from PIC import PIC


class Risque:
    user = None
    password = None
    session = None

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.session = requests.session()

    def getTicketData(self, ticketNumber):
        try:
            ticket = self.getTicketBody(ticketNumber)
            # actually parsing the data
        except ValueError:
            print "Failed to get ticket, login invalid"
            return None

    def getTicketBody(self, ticketNumber):
        login = self.session.get(
            'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal')
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

        form['username'] = self.username
        form['password'] = self.password

        response = self.session.post(
            'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal',
            data=form)
        ticket = self.session.get('https://risque.itap.purdue.edu/Tickets/Data/TicketDetail.aspx?id=%s' % ticketNumber)

        txt = ticket.content
        if "You have asked to login to" in txt:
            raise ValueError("Failed to get ticket body, login invalid")
        return txt

    # Returns a cleaned version of the string
    def clean(self, string):
        if string is None:
            return string
        if type(string) is not str and type(string) is not unicode and type(string) is not NavigableString:
            raise AttributeError("string attribute is an invalid type")
        value = re.sub('[\t\n\xa0]', '', string).strip().encode('ascii', 'replace')
        if value == 'None':
            return None
        return value

    # Returns a Ticket object
    def parseTicket(self, ticketBody):
        if ticketBody is None or type(ticketBody) is not str:
            raise AttributeError("ticketBody attribute is invalid")
        try:
            data = BeautifulSoup(ticketBody, 'html.parser')
            dueby = self.clean(data.find('span', {'id': 'contentMain_lblTicketDue'}).string)
            priority = self.clean(data.find('span', {'id': 'contentMain_lblTicketPriority'}).string)
            status = self.clean(data.find('span', {'id': 'contentMain_lblTicketStatus'}).string)
            number = self.clean(data.find('span', {'id': 'contentMain_lblTicketID'}).string)
            ticket = Ticket(number, dueby, priority, status)
            # Parse the items
            table = data.find('table', {'id': 'contentMain_grdItems'})
            rows = table.find_all('tr')     # row[0] is a header row

            # Iterate over the table
            for i in range(1, len(rows)):
                j = i - 1       # Reindex i to start at 0 instead of 1
                cols = rows[i].find_all('td') # rows[3] is an options row
                action = self.clean(cols[0].strong.string)
                picId = cols[1].find('a', {'id': 'contentMain_grdItems_PICHyperLink_' + str(j)}).string
                patch = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemPatch_' + str(j)}).string
                currentProvider = \
                cols[1].find('div', {'id': 'contentMain_grdItems_PanelCurrentProviderPort_' + str(j)}).contents[3]
                #  newProvider = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemProvider_' + str(j)}).string
                newProvider = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemProvider_' + str(j)})
                if newProvider is not None:
                    newProvider = newProvider.string
                else:
                    raise ValueError("Ticket contains a null 'New Provider' field")
                # currentSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldSpeed_' + str(j)}).contents[1]
                currentSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldSpeed_' + str(j)})
                if currentSpeed is not None:
                    currentSpeed = currentSpeed.contents[1]
                else:
                    currentSpeed = None
                # currentVlans = cols[2].find('span', {
                    # 'id': 'contentMain_grdItems_lblItemOldVLAN_' + str(j)}).contents  # contents[0] is <br/>
                currentVlans = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldVLAN_' + str(j)})
                if currentVlans is not None:
                    currentVlans = currentVlans.contents
                else:
                    currentVlans = None
                # currentVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblCurrentVoIPVlan_' + str(j)}).contents[1]
                currentVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblCurrentVoIPVlan_' + str(j)})
                if currentVoip is not None and len(currentVoip) >= 2:
                    currentVoip = currentVoip.contents[1]
                else:
                    currentVoip = None
                newSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemNewSpeed_' + str(j)}).contents[1]
                newVlans = cols[2].find('span', {
                    'id': 'contentMain_grdItems_lblItemNewVLAN_' + str(j)}).contents  # contents[0] is <br/>
                # newVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblNewVoIPVlan_' + str(j)}).contents[1]
                newVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblNewVoIPVlan_' + str(j)})
                if newVoip is not None and len(newVoip.contents) >= 2:
                        newVoip = newVoip.contents[1]
                else:
                    newVoip = None
                newServices = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemServices_' + str(j)}).string
                # Clean the data
                pidId = self.clean(picId)
                patch = self.clean(patch)
                currentProvider = self.clean(currentProvider)
                newProvider = self.clean(newProvider)
                currentSpeed = self.clean(currentSpeed)
                if currentVlans is not None:
                    for x in range(1, len(currentVlans)):
                        currentVlans[x] = self.clean(currentVlans[x])
                    del currentVlans[0]
                currentVoip = self.clean(currentVoip)
                newSpeed = self.clean(newSpeed)
                for x in range(1, len(newVlans)):
                    newVlans[x] = self.clean(newVlans[x])
                del newVlans[0]
                newVoip = self.clean(newVoip)
                # Don't clean new services as we're not sure if it is a str or []

                # Add Actions
                pic = PIC(picId, currentProvider, newProvider, action, newServices)
                if currentVlans is not None and currentSpeed is not None:
                    pic.applyCurrentConfig(currentVoip, currentVlans, currentSpeed)
                pic.applyNewConfig(newVoip, newVlans, newSpeed)
                ticket.addPic(pic)

            return ticket
        except:
            raise
