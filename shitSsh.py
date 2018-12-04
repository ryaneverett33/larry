import paramiko


# The shittiest ssh imaginable
# This works for switches and it sucks
class shitSsh:

    @staticmethod
    def execute(command, host, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
