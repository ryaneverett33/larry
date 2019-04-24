class Services:
    # List of Services
    # Allow DHCP Server
    # Disable BPDU Guard
    # Disable CDP Neighbor
    # Disable Power over Ethernet
    # Disable Voice VLAN (VoIP)
    # Port Channel [Don't allow larry to do]
    allowDHCP = False
    disableBPDU = False
    disableCDP = False
    disablePOE = False
    disableVoIP = False

    def __init__(self, services):
        if services is not None:
            self.__parseServices(services)

    def __parseServices(self, services):
        for service in services:
            if "DHCP" in service:
                self.allowDHCP = True
            elif "BPDU" in service:
                self.disableBPDU = True
            elif "CDP" in service:
                self.disableCDP = True
            elif "Power" in service:
                self.disablePOE = True
            elif "Voice" in service:
                self.disableVoIP = True

