import paramiko
import time
from Logger import Logger
from COMMON import Common
from socket import timeout


class Ssh:
    MAX_WAIT_ATTEMPTS = 5
    MAX_SEND_ATTEMPTS = 15
    BUFFER_LEN = 1000

    host = None
    hostname = None
    cleanedHostname = None
    user = None
    password = None
    client = None
    connected = False
    channel = None
    expected = ""
    SSH_DISALLOWED_HOSTS = ["lynn-sbpe", "erht-sbpe"]   # itap-iape and lamb-sbpe have FEX ports
    SSH_FEX_HOST = ["itap-iape", "lamb-sbpe"]
    SSH_TIMEOUT = 10                                     # avoid forever waiting for ssh
    SSH_VRF_TIMEOUT = 3                                  # reduce timeout for vrf
    SSH_DIRTY_COMMAND = 'ls'
    vrfAffected = False

    # Enable Mode versus NonEnabled Mode
    modes = {
        '#',
        '>'
    }
    logger = None

    # Password is not the boilerkey password
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.logger = Logger.getInstance(None)

    # Connects to the host if a host is not already connected
    def connect(self, host):
        # print "SSH Driver connecting to {0}".format(host)
        self.logger.logSSH("SSH Driver connecting to {0}".format(host))
        if self.connected:
            raise StandardError("Already connected to a host, must disconnect first")
        else:
            self.client.connect(host, username=self.user, password=self.password, look_for_keys=False)
            self.channel = self.client.invoke_shell(term="vt100", height=500)
            self.connected = True
            self.host = host
            if Common.isHostVrfAffected(host):
                self.vrfAffected = True
                self.channel.settimeout(self.SSH_VRF_TIMEOUT)
                self.logger.logSSH("Host {0} is vrf affected, new timeout: {1}".format(self.host, self.SSH_VRF_TIMEOUT))
            else:
                self.channel.settimeout(self.SSH_TIMEOUT)
                self.logger.logSSH("Host {0} is not vrf affected, new timeout: {1}".format(self.host, self.SSH_TIMEOUT))
            self.findIOSHostname()

    # Disconnects from the current host
    def disconnect(self):
        if not self.connected:
            raise StandardError("Not connected to a host, must be connected first")
        else:
            self.channel.shutdown(2)
            self.client.close()
            self.connected = False

    def getPeerName(self):
        return self.channel.getpeername()[0]

    # Waits for the channel to become send ready for a max number of attempts
    # Raises a RuntimeError if attempts are exceeded
    def __waitForSendReady(self):
        waitAttempts = 0
        while not self.channel.send_ready():
            if waitAttempts == self.MAX_WAIT_ATTEMPTS:
                raise RuntimeError("SSH Channel timed out, MAX_WAIT_ATTEMPTS")
            waitAttempts = waitAttempts + 1
            time.sleep(1)

    # Waits for the channel to become receive ready for a max number of attempts
    # Raises a RuntimeError if attempts are exceeded
    def __waitForRecvReady(self):
        waitAttempts = 0
        while not self.channel.recv_ready():
            if waitAttempts == self.MAX_WAIT_ATTEMPTS:
                raise RuntimeError("SSH Channel timed out, MAX_WAIT_ATTEMPTS")
            waitAttempts = waitAttempts + 1
            time.sleep(1)

    def __send(self, message):
        return self.channel.sendall(message + '\n')

    def setExpect(self, expected):
        self.expected = expected

    # Return the hostname of the ios system
    # keepMode determines whether or not mode symbols should be kept
    def findIOSHostname(self, keepMode=False):
        self.__waitForSendReady()
        self.__send('\n')
        self.__waitForRecvReady()
        recieved = self.channel.recv(self.BUFFER_LEN)
        hostname = recieved
        if '\n' in recieved:
            recvSplit = recieved.split('\n')
            # find in array
            found = False
            for split in recvSplit:
                if split == '\r' or len(split) is 0:
                    continue
                hostname = split
                found = True
                break
            if not found:
                # print "UNABLE TO FIND HOSTNAME"
                self.logger.logSSH("UNABLE TO FIND HOSTNAME")
        if '\r' in hostname:
            hostname = hostname.split('\r')[0]
        if not keepMode:
            modeChar = hostname[len(hostname) - 1]
            for mode in self.modes:
                if modeChar == mode:
                    hostname = hostname[0:len(hostname)-1]
                    break
        self.hostname = hostname
        self.cleanHostname()
        self.logger.logSSH("IOS Hostname: {0}".format(self.hostname))
        return self.hostname

    # Fix for mjis-3063-c9348uxm-01.tcom.purdue.edu, where config t -> mjis-3063-c9348uxm-0(config)#
    def cleanHostname(self):
        hostSplit = self.hostname.split('-')
        hostClean = ""
        for i in range(0, len(hostSplit) - 1):
            hostClean = hostClean + hostSplit[i]
            if i < len(hostSplit) - 2:
                hostClean = hostClean + '-'
        self.cleanedHostname = hostClean

    def execute(self, command):
        try:
            if self.vrfAffected:

                if '\n' in command:
                    # multiline command, things break
                    brokenCommands = command.split('\n')
                    self.logger.logSSH("Multi-line command on a VRF Affected host, split into {0} commands".format(len(brokenCommands)))
                    result = None
                    for brokenCommand in brokenCommands:
                        result = self.dirtyExecute(brokenCommand)
                    return result
                else:
                    return self.dirtyExecute(command)
            else:
                return self.cleanExecute(command)
        except timeout:
            self.logger.logSSH("Failed to execute {0}, socket timedout".format(command))
        except Exception, e:
            self.logger.logSSH("Failed to execute {0}, exception: {1}".format(command, e))

    # Executes the command and returns [cleaned output, resultant hostname]
    # Commands are appended with a newline
    def cleanExecute(self, command):
        if not self.connected:
            # print "not connected to a host, can't execute"
            self.logger.logSSH("not connected to a host, can't execute")
            return
        # print "Ssh Driver executing command {0}".format(command)
        self.logger.logSSH("Ssh Driver executing command {0}".format(command))
        self.__waitForSendReady()
        self.__send(command)
        self.__waitForRecvReady()

        foundHostname = False
        output = ""
        while not foundHostname:
            rawOutput = self.channel.recv(self.BUFFER_LEN)
            # print "\trawOutput: {0}".format(rawOutput)
            outputLines = rawOutput.split('\n')
            for line in outputLines:
                if '\r' in line:
                    line = line.split('\r')[0]
                if len(line) == 0:
                    continue
                if "more" in line.lower():
                    self.__send(' ')
                    # print "REQUESTING MORE, SENDING NEWLINE, line: {0}".format(line)
                    continue
                if command in line:
                    continue
                if self.hostname in line or self.cleanedHostname in line:
                    # print "FOUND HOSTNAME: {0} on line {1}".format(self.hostname, line)
                    foundHostname = True
                    return [output[0:len(output)-1], line]
                output = output + line + '\n'
            if not foundHostname:
                if len(output) > 1 and output[len(output) - 1] == '\n':
                    output = output[0:len(output) - 1]
        # buffer = ""
        # finishedRecieving = False
        # while not finishedRecieving:
        #     text = self.channel.recv(self.BUFFER_LEN)
            # check if text contains the expected string

    # Workaround for VRF affected hosts: send clean command and don't wait for output, send dirty command and retrieve output
    def dirtyExecute(self, command):
        if not self.connected:
            # print "not connected to a host, can't execute"
            self.logger.logSSH("not connected to a host, can't execute")
            return
        # print "Ssh Driver executing command {0}".format(command)
        self.logger.logSSH("Ssh Driver executing clean command `{0}`".format(command))
        self.__waitForSendReady()
        self.__send(command)
        self.__waitForRecvReady()
        self.channel.recv(self.BUFFER_LEN)
        self.__waitForSendReady()
        self.logger.logSSH("Ssh Driver executing dirty command `{0}`".format(self.SSH_DIRTY_COMMAND))
        response = self.cleanExecute(self.SSH_DIRTY_COMMAND)
        lines = response[0].split('\n')
        # strip out the last three lines
        newLines = []
        foundCarrot = False
        foundInvalid = False
        for line in lines:
            if line.strip() == '^' and not foundCarrot:
                foundCarrot = True
                continue
            elif "Invalid input" in line and not foundInvalid:
                foundInvalid = True
                continue
            newLines.append(line)
        # flatten lines
        flattened = ""
        for i in range(0, len(newLines)):
            flattened = flattened + newLines[i]
            if i != len(newLines)-1:
                flattened = flattened + '\n'
        response[0] = flattened
        return response

    def isForbiddenHost(self):
        for host in self.SSH_DISALLOWED_HOSTS:
            if host in self.hostname:
                return True
        return False

    def isFexHost(self):
        for host in self.SSH_FEX_HOST:
            if host in self.hostname:
                return True
        return False
