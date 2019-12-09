import requests, lxml.html
import re
from bs4 import BeautifulSoup, NavigableString, Tag
from Ticket import Ticket
from PIC import PIC
import warnings
from ConfigurationDriver import ConfigurationDriver
from PasswordUtility import PasswordUtility
import SingeltonManager


class Risque:
    username = None
    password = None
    session = None
    loggedIn = False
    loadedSession = False

    def __init__(self, user, password):
        self.username = user
        self.password = password
        self.session = requests.session()
        warnings.filterwarnings("ignore")

    def getTicketData(self, ticketNumber):
        try:
            ticket = self.getTicketBody(ticketNumber)
            return self.parseTicket(ticket)
        except ValueError:
            print "Failed to get ticket, login invalid"
            result = raw_input("Failed to login to risque, change risque password? (y/n)")
            if result.lower() == "y":
                newRisquePass = PasswordUtility.getpassword("Risque Password (BoilerKey): ")
                user, risquePass, switchPass = ConfigurationDriver.getCredentials()
                ConfigurationDriver.storeCredentials(user, newRisquePass, switchPass)
            ConfigurationDriver.clearCookies()
            return None

    def testSession(self):
        data = None
        if ConfigurationDriver.cookiesStored():
            data = self.session.get('https://risque.itap.purdue.edu', cookies=ConfigurationDriver.getCookies())
        else:
            return False
        if "login" in data.url:
            return False
        return True

    def getTicketBody(self, ticketNumber):
        # if not self.loadedSession:
        #     if self.testSession():
        #         self.loadedSession = True
        #         ConfigurationDriver.saveSession()
        #     else:
        #         self.login()
        if not ConfigurationDriver.loadedSession:
            self.login()
        ticket = None
        if ConfigurationDriver.cookiesStored():
            ticket = self.session.get('https://risque.itap.purdue.edu/Tickets/Data/TicketDetail.aspx?id=%s' % ticketNumber,
                                      cookies=ConfigurationDriver.getCookies())
        else:
            ticket = self.session.get(
                'https://risque.itap.purdue.edu/Tickets/Data/TicketDetail.aspx?id=%s' % ticketNumber)
            ConfigurationDriver.storeCookies(self.session.cookies)

        txt = ticket.content
        # Store session
        if "You have asked to login to" in txt:
            raise ValueError("Failed to get ticket body, login invalid")
        else:
            if not ConfigurationDriver.loadedSession:
                persist = SingeltonManager.getPersistenceModule()
                if persist is not None:
                    persist.save()
        return txt

    # Returns a cleaned version of the string
    def clean(self, string):
        if string is None:
            return string
        if type(string) is not str and type(string) is not unicode and type(string) is not NavigableString:
            raise AttributeError("string attribute is an invalid type")
        value = re.sub('[\t\n\xa0]', '', string).strip().encode('ascii', 'replace')
        if value == 'None' or value == '' or value.lower() == 'n/a':
            return None
        return value

    def login(self):
        print "Logging in"
        login = self.session.get(
            # 'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal')
            'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal%2fLoginHelperRisque.aspx%3fredirecturl%3dhttps%253a%252f%252frisque.itap.purdue.edu%252fPortal%252fDefault.aspx&renew=true')
        login_html = lxml.html.fromstring(login.text)
        # hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        hidden_inputs = login_html.xpath(r'//form//input')
        form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}

        form['username'] = self.username
        form['password'] = self.password

        response = self.session.post(
            # 'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal',
            'https://www.purdue.edu/apps/account/cas/login?service=https%3a%2f%2frisque.itap.purdue.edu%2fPortal%2fLoginHelperRisque.aspx%3fredirecturl%3dhttps%253a%252f%252frisque.itap.purdue.edu%252fPortal%252fDefault.aspx&renew=true',
            data=form)
        self.loggedIn = True

    # Return a list that doesn't contain any Tag Objects
    def __removeTags(self, list):
        newList = []
        for item in list:
            if not isinstance(item, Tag):
                newList.append(item)
        return newList

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
                cols = rows[i].find_all('td')   # rows[3] is an options row
                action = self.clean(cols[0].strong.string)
                picId = cols[1].find('a', {'id': 'contentMain_grdItems_PICHyperLink_' + str(j)}).string
                patch = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemPatch_' + str(j)}).string
                currentProvider = cols[1].find('div', {'id': 'contentMain_grdItems_PanelCurrentProviderPort_' + str(j)})
                if currentProvider is not None:
                    currentProvider = currentProvider.contents[3]
                #  newProvider = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemProvider_' + str(j)}).string
                newProvider = cols[1].find('span', {'id': 'contentMain_grdItems_lblItemProvider_' + str(j)})
                if newProvider is not None:
                    newProvider = newProvider.string
                # else:
                #    raise ValueError("Ticket contains a null 'New Provider' field")
                # currentSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldSpeed_' + str(j)}).contents[1]
                currentSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldSpeed_' + str(j)})
                if currentSpeed is not None:
                    currentSpeed = currentSpeed.contents[1]
                else:
                    currentSpeed = None
                # currentVlans = cols[2].find('span', {
                    # 'id': 'contentMain_grdItems_lblItemOldVLAN_' + str(j)}).contents  # contents[0] is <br/>
                currentVlans = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldVLAN_' + str(j)})
                if currentVlans is not None and len(currentVlans) >= 2:
                    currentVlans = currentVlans.contents
                else:
                    currentVlans = None
                # currentVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblCurrentVoIPVlan_' + str(j)}).contents[1]
                currentVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblCurrentVoIPVlan_' + str(j)})
                if currentVoip is not None and len(currentVoip) >= 2:
                    currentVoip = currentVoip.contents[1]
                else:
                    currentVoip = None
                currentServices = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemOldServices_' + str(j)})
                if currentServices is not None:
                    currentServices = currentServices.contents
                # newSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemNewSpeed_' + str(j)}).contents[1]
                newSpeed = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemNewSpeed_' + str(j)})
                if newSpeed is not None:
                    newSpeed = newSpeed.contents[1]
                # newVlans = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemNewVLAN_' + str(j)}).contents  # contents[0] is <br/>
                newVlans = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemNewVLAN_' + str(j)})
                if newVlans is not None and len(newVlans.contents) >= 2:
                    newVlans = newVlans.contents
                else:
                    newVlans = None
                newTaggedVlans = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemTaggedVLANs_' + str(j)})
                if newTaggedVlans is not None and len(newTaggedVlans.contents) >= 2:
                    newTaggedVlans = newTaggedVlans.contents
                else:
                    newTaggedVlans = None
                # newVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblNewVoIPVlan_' + str(j)}).contents[1]
                newVoip = cols[2].find('span', {'id': 'contentMain_grdItems_lblNewVoIPVlan_' + str(j)})
                if newVoip is not None and len(newVoip.contents) >= 2:
                        newVoip = newVoip.contents[1]
                else:
                    newVoip = None
                # newServices = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemServices_' + str(j)}).string
                newServices = cols[2].find('span', {'id': 'contentMain_grdItems_lblItemServices_' + str(j)})
                if newServices is not None:
                    if newServices.string == "None":
                        newServices = None
                    else:
                        newServices = newServices.contents

                # Clean the data
                pidId = self.clean(picId)
                patch = self.clean(patch)
                currentProvider = self.clean(currentProvider)
                newProvider = self.clean(newProvider)
                currentSpeed = self.clean(currentSpeed)
                if currentVlans is not None:
                    currentVlans = self.__removeTags(currentVlans)
                    for x in range(0, len(currentVlans)):
                        currentVlans[x] = self.clean(currentVlans[x])
                    if len(currentVlans) == 1:
                        # convert from list
                        currentVlans = currentVlans[0]
                currentVoip = self.clean(currentVoip)
                newSpeed = self.clean(newSpeed)
                if newVlans is not None:
                    for x in range(0, len(newVlans)):
                        if isinstance(newVlans[x], NavigableString):
                            newVlans[x] = self.clean(newVlans[x])
                    newVlans = self.__removeTags(newVlans)
                    if len(newVlans) == 1:
                        # convert from list
                        newVlans = newVlans[0]
                if newTaggedVlans is not None:
                    newTaggedVlans = self.__removeTags(newTaggedVlans)
                    for x in range(0, len(newTaggedVlans)):
                        if isinstance(newTaggedVlans[x], NavigableString):
                            newTaggedVlans[x] = self.clean(newTaggedVlans[x])
                if currentServices is not None:
                    currentServices = self.__removeTags(currentServices)
                    for x in range(0, len(currentServices)):
                        if isinstance(currentServices[x], NavigableString):
                            currentServices[x] = self.clean(currentServices[x])
                if newServices is not None:
                    newServices = self.__removeTags(newServices)
                    for x in range(0, len(newServices)):
                        if isinstance(newServices[x], NavigableString):
                            newServices[x] = self.clean(newServices[x])
                newVoip = self.clean(newVoip)
                # Don't clean new services as we're not sure if it is a str or []

                # Add Actions
                pic = PIC(picId, currentProvider, newProvider, action)

                if currentVlans is not None and currentSpeed is not None:
                    pic.applyCurrentConfig(currentVoip, currentVlans, currentSpeed)
                if currentServices is not None:
                    pic.addServices(False, currentServices)
                if newTaggedVlans is not None and newSpeed is not None:
                    pic.applyNewConfig(newVoip, newVlans, newSpeed)
                    pic.addTaggedVlans(newTaggedVlans)
                elif newVlans is not None and newSpeed is not None:
                    pic.applyNewConfig(newVoip, newVlans, newSpeed)
                if newTaggedVlans is not None:
                    pic.addTaggedVlans(newTaggedVlans)
                if newServices is not None:
                    pic.addServices(True, newServices)
                if patch is not None:
                    pic.addPatchPanel(patch)
                ticket.addPic(pic)

            return ticket
        except:
            raise
