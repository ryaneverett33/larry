import paramiko
import time


# Keeps a buffer of opened channels for communicating
class BufferedSsh:
    CHANNEL_SIZE = 1        # number of channels to open

    user = None
    password = None
    host = None
    connected = False
    channels = []
    client = None

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self.client = paramiko.client.SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    def connect(self, host):
        if self.connected:
            raise StandardError("Already connected to a host, must disconnect first")
        else:
            # Create a client and start opening channels
            self.host = host
            self.connected = True
            self.client.connect(host, username=self.user, password=self.password, look_for_keys=False)
            self.__populateChannels()

    def disconnect(self):
        if not self.connected:
            raise StandardError("Not connected to a host, must be connected first")
        else:
            self.host = None
            self.connected = False
            for channel in self.channels:
                channel.shutdown(2)
            self.client.close()

    def __populateChannels(self):
        print "populating channels"
        for i in range(0, self.CHANNEL_SIZE):
            print "create channel {0}".format(i)
            channel = self.client.get_transport().open_session()
            if channel is None:
                print "open_session returned None"
            self.channels.append(channel)

    def __getChannel(self):
        if len(self.channels) == 0:
            # open more channels
            self.__populateChannels()
        return self.channels.pop()

    def exec_command(self, command):
        channel = self.__getChannel()
        channel.exec_command(command)
        stdin = channel.makefile("wb", -1)
        stdout = channel.makefile("r", -1)
        stderr = channel.makefile_stderr("r", -1)
        return stdin, stdout, stderr
