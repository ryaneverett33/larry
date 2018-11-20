from PIC import PIC
from risque import risque

class Ticket:
    number = None
    pics = None
    picNames = None     # [name] -> PIC object

    def __init__(self, number):
        self.number = number
        self.pics = []
        self.picNames = dict()

    def __containsPic(self, pic):
        return self.picNames.has_key(pic)

    def __sort(self):
        self.pics = sorted(self.pics, cmp=lambda x, y: (y.TR < x.TR) - (y.TR > x.TR))

    def addPic(self, pic):
        if isinstance(pic) != PIC:
            raise AttributeError("Can't add a pic that isn't of type PIC")
        if not self.__containsPic(pic):
            self.pics.append(pic)
            self.picNames[pic.name] = pic
            self.__sort()
        else:
            raise ValueError("PIC already added")

