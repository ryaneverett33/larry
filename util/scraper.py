import sys
sys.path.insert(0, "../")
import getpass
from Risque import Risque


def listToStr(list):
    value = ""
    for i in range(0, len(list)):
        vlan = list[i]
        value = value + vlan.__str__()
        if i < len(list) - 1:
            value = value + ', '
    return value


def printTicket(ticket):
    print "Ticket #{0}, Dueby: {1}, Priority: {2}, status: {3}".format(ticket.number, ticket.dueby, ticket.priority, ticket.status)
    print ""
    for i in range(0, len(ticket.pics)):
        pic = ticket.pics[i]
        print "PIC: {0}, Action: {1}, Current Provider: {2}, New Provider: {3}"\
            .format(pic.name, pic.action, pic.currentProvider, pic.newProvider)
        if pic.currentConfig is not None:
            print "Current Speed: {0}, Current Vlans: {1}, Trunk: {3} Current VoIP: {2}"\
                .format(pic.currentConfig.speed, listToStr(pic.currentConfig.vlan), pic.currentConfig.voiceVlan,
                        pic.currentConfig.trunk)
        else:
            print "Current Speed: None, Current Vlans: None, Current VoIP: None"
        if pic.newConfig is not None:
            print "New Speed: {0}, New Vlans: {1}, Trunk: {4} New VoIP: {2}, New Services: {3}"\
                .format(pic.newConfig.speed, listToStr(pic.newConfig.vlan), pic.newConfig.voiceVlan, pic.services,
                        pic.newConfig.trunk)
        else:
            print "New Speed: None, New Vlans: None, New VoIP: None"
        print ""


def loadFile(filepath):
    f = open(filepath, 'r')
    return f.read()


def main():
    textBody = None
    r = None
    if len(sys.argv) > 1:
        # filepath supplied
        filepath = sys.argv[1]
        print "Loading HTML from {0}".format(filepath)
        textBody = loadFile(filepath)
        r = Risque('u', 'p')
    else:
        username = raw_input("Username: ")
        password = getpass.getpass("Password(BoilerKey): ")
        ticketNumber = raw_input("Ticket number: ")
        try:
            r = Risque(username, password)
            textBody = r.getTicketBody(ticketNumber)
        except Exception, e:
            print "Unable to grab ticket from risque"
            print sys.exc_info()
            sys.exit(-1)
    ticket = r.parseTicket(textBody)
    printTicket(ticket)


if __name__ == "__main__":
    main()