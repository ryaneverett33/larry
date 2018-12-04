import paramiko
import time


# Keeps a buffer of opened clients
# This only works for glitch, so it can't be used
class BufferedSshClients:
    CLIENT_COUNT = 1        # number of channels to open

    user = None
    password = None
    host = None
    connected = False
    clients = []

    def __init__(self, user, password):
        self.user = user
        self.password = password
        # self.client = paramiko.client.SSHClient()
        # self.client.load_system_host_keys()
        # self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())

    def connect(self, host):
        if self.connected:
            raise StandardError("Already connected to a host, must disconnect first")
        else:
            # Create a client and start opening channels
            self.host = host
            self.connected = True
            # self.client.connect(host, username=self.user, password=self.password, look_for_keys=False)
            self.__populateClients()

    def disconnect(self):
        if not self.connected:
            raise StandardError("Not connected to a host, must be connected first")
        else:
            self.host = None
            self.connected = False
            # for channel in self.channels:
            #    channel.shutdown(2)
            # self.client.close()
            while len(self.clients) > 0:
                client = self.clients.pop()
                client.close()

    def __populateClients(self):
        print "populating clients"
        for i in range(0, self.CLIENT_COUNT):
            print "create client {0}".format(i)
            client = self.__createClient(self.host)
            if client is None:
                print "createClient failed to create a client"
            else:
                self.clients.append(client)
            # channel = self.client.get_transport().open_session()
            # if channel is None:
            #     print "open_session returned None"
            # self.channels.append(channel)

    def __getClient(self):
        if len(self.clients) == 0:
            # open more channels
            self.__populateClients()
        return self.clients.pop()

    # Creates a new connected client
    def __createClient(self, host):
        client = paramiko.client.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        client.connect(host, username=self.user, password=self.password, look_for_keys=False)
        return client

    def exec_command(self, command):
        # client = self.__getClient()
        # stdin, stdout, stderr = client.exec_command(command, get_pty=True)
        # return stdin, stdout, stderr
        client = self.__getClient()
        channel = client.get_transport().open_session()
        channel.exec_command(command)
        stdin = channel.makefile("wb", -1)
        stdout = channel.makefile("r", -1)
        stderr = channel.makefile_stderr("r", -1)
        return stdin, stdout, stderr
