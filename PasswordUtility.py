import getpass


class PasswordUtility:
    inEditor = False

    @staticmethod
    def getpassword(prompt):
        if PasswordUtility.inEditor:
            return raw_input(prompt)
        else:
            return getpass.getpass(prompt)

    @staticmethod
    def useEditor():
        PasswordUtility.inEditor = True
