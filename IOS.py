from Ssh import Ssh


# Represents an SSH connection to an IOS switch
class IOS:
    sshClient = None
    host = None
    switchType = None   # e.g. c3750ep

    def __init__(self, sshClient, host, switchType):
        self.sshClient = sshClient
        if self.sshClient.connected:
            self.sshClient.disconnect()
        self.sshClient.connect(host)
        self.switchType = switchType

    def sis(self):
        # [output, hostname]
        result = self.sshClient.execute('sis')

    def __isValidResponse(self, commandResponse):
        return (True, False)["Invalid input" in commandResponse]

    def __flatten(self, arr, char='\n'):
        string = ""
        for i in arr:
            string = string + i
            string = string + char
        return string

    # return an array of lines
    def getConfig(self, interface, flatten=True):
        switchConfig = self.sshClient.execute("show run int {0}".format(interface))[0]
        if not self.__isValidResponse(switchConfig):
            print "Failed to get switch config, {0} may be invalid".format(interface)
            return None
        # clean up lines
        lines = []
        rawLines = switchConfig.split('\n')
        for line in rawLines:
            if "Current configuration" in line:
                continue
            if "Building configuration" in line:
                continue
            if line == "!":
                continue
            if "interface" in line:
                continue
            if "end" in line:
                continue
            lines.append(line.strip())
        if flatten:
            return self.__flatten(lines)
        else:
            return lines

    def currentMode(self):
        a = None

