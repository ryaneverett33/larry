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
    serviceCount = 0

    def __init__(self, services):
        if services is not None:
            self.__parseServices(services)

    def __parseServices(self, services):
        for service in services:
            if "DHCP" in service:
                self.allowDHCP = True
                self.serviceCount = self.serviceCount + 1
            elif "BPDU" in service:
                self.disableBPDU = True
                self.serviceCount = self.serviceCount + 1
            elif "CDP" in service:
                self.disableCDP = True
                self.serviceCount = self.serviceCount + 1
            elif "Power" in service:
                self.disablePOE = True
                self.serviceCount = self.serviceCount + 1
            elif "Voice" in service:
                self.disableVoIP = True
                self.serviceCount = self.serviceCount + 1

    def __str__(self):
        if self.serviceCount == 0:
            return "None"
        string = "["
        currentCount = 0
        if self.allowDHCP:
            string = string + "Allow DHCP Server"
            currentCount = currentCount + 1
            if currentCount != self.serviceCount:
                string = string + ", "
        if self.disableBPDU:
            string = string + "Allow DHCP Server"
            currentCount = currentCount + 1
            if currentCount != self.serviceCount:
                string = string + ", "
        if self.disableCDP:
            string = string + "Allow DHCP Server"
            currentCount = currentCount + 1
            if currentCount != self.serviceCount:
                string = string + ", "
        if self.disablePOE:
            string = string + "Allow DHCP Server"
            currentCount = currentCount + 1
            if currentCount != self.serviceCount:
                string = string + ", "
        if self.disableVoIP:
            string = string + "Allow DHCP Server"
            currentCount = currentCount + 1
            if currentCount != self.serviceCount:
                string = string + ", "
        return string + "]"
