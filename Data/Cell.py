from graphics import *
from math import pi, sqrt
from random import randint
from copy import copy, deepcopy


class Cell(Rectangle):
    def __init__(self, p1, p2, infectionFraction, settings, simSizeArray):
        super().__init__(p1, p2)

        # Create object attributes
        self.infFraction = round(float(infectionFraction), 4)
        self.simSettings = settings
        self.xPos = int(self.getP1().getX()) / int(self.getSetting("COORD_SCALING"))
        self.yPos = int(self.getP1().getY()) / int(self.getSetting("COORD_SCALING"))
        self.isInfected = False
        self.population = 0
        self.infectedPop = 0
        self.age = 0
        self.simSizeX = simSizeArray[0]
        self.simSizeY = simSizeArray[1]
        self.isUrban = self.checkUrban()
        self.amountOfMasksType1 = 0
        self.amountOfMasksType2 = 0
        self.amountOfMasksType3 = 0

    def calcUrbanRadius(self):
        A = int(self.getSetting("URBAN_AREA"))
        r = sqrt(A / pi)
        return r

    def calcDistFromCentre(self):
        centreX = self.simSizeX / 2
        centreY = self.simSizeY / 2
        dist = sqrt((abs(self.xPos - centreX)) ** 2 + (abs(self.yPos - centreY)) ** 2)
        return dist

    def checkUrban(self):
        uRad = self.calcUrbanRadius()
        dist = self.calcDistFromCentre()
        if dist <= (uRad - 3):
            urban = True
        elif (uRad - 3) < dist <= (uRad + 3):
            rand = randint(0, 1)
            if rand == 0:
                urban = False
            elif rand == 1:
                urban = True
            else:
                raise ValueError("While determining if cell was urban, randint produced %s" % rand)
        elif dist > (uRad + 3):
            urban = False
        else:
            raise ValueError("Dist is not in range of playing field. dist = %s" % dist)
        return urban

    def getSetting(self, setting):
        value = self.simSettings[self.simSettings.index(setting) + 1]

        return value

    def __deepcopy__(self, memo):
        cellCopy = type(self)(
            deepcopy(self.p1),
            deepcopy(self.p2),
            deepcopy(self.infFraction),
            deepcopy(self.simSettings),
            deepcopy([self.simSizeX, self.simSizeY]))
        cellCopy.__dict__.update(self.__dict__)

        return cellCopy
