import paramiko
import time


class Ssh:
    MAX_WAIT_ATTEMPTS = 5
    MAX_SEND_ATTEMPTS = 15
    BUFFER_LEN = 1000

    host = None
    user = None
    password = None
    client = None
    connected = False
    channel = None
    expected = ""

    # Password is not the boilerkey password
    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    # Connects to the host if a host is not already connected
    def connect(self, host):
        if self.connected:
            raise StandardError("Already connected to a host, must disconnect first")
        else:
            self.client.connect(host, username=self.user, password=self.password, look_for_keys=False)
            self.channel = self.client.invoke_shell(term="vt100", height=500)
            self.connected = True

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
    def findIOSHostname(self):
        self.__waitForSendReady()
        self.__send('\n')
        self.__waitForRecvReady()
        recieved = self.channel.recv(self.BUFFER_LEN)
        return recieved

    # Executes the command and returns the result (stdout)
    # Commands are appended with a newline
    def execute(self, command, more=True):
        self.__waitForSendReady()
        self.__send(command)
        self.__waitForRecvReady()
        return self.channel.recv(self.BUFFER_LEN)
        # buffer = ""
        # finishedRecieving = False
        # while not finishedRecieving:
        #     text = self.channel.recv(self.BUFFER_LEN)
            # check if text contains the expected string
