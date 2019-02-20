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
        raise NotImplementedError()
