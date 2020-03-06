from Data.Cell import *
import csv
import copy
import random


class Simulation:
    def __init__(self, simulationSettings):
        # Create object attributes
        self.simSettings = simulationSettings
        self.simSizeX = 0
        self.simSizeY = 0
        self.cells = []

        # Stats to track
        self.population = 0
        self.totCases = 0
        self.percentageInfected = 0
        self.newInfected = 0
        self.totInfected = 0
        self.totDead = 0
        self.newDead = 0
        self.totRecovered = 0
        self.newRecovered = 0

        # Load Settings
        self.uArea = int(self.getSetting("URBAN_AREA"))
        self.surrArea = int(self.getSetting("SURROUNDING_AREA"))
        self.uPop = int(self.getSetting("URBAN_POPULATION"))
        self.surrPop = int(self.getSetting("SURROUNDING_POPULATION"))
        self.graphMode = int(self.getSetting("WHAT_TO_GRAPH"))
        self.coordScale = int(self.getSetting("COORD_SCALING"))
        self.createFile = int(self.getSetting("CREATE_DATA_FILE"))
        self.spreadRate = float(self.getSetting("SPREAD_RATE"))
        self.minIncubation = int(self.getSetting("MIN_INCUBATION_PERIOD"))
        self.maxIncubation = int(self.getSetting("MAX_INCUBATION_PERIOD"))
        self.recTime = int(self.getSetting("RECOVERY_TIME"))
        self.deathRate = float(self.getSetting("DEATH_RATE"))
        self.recRate = float(self.getSetting("RECOVERY_RATE"))
        self.reductionRate = float(self.getSetting("REDUCTION_RATE"))
        self.runTime = int(self.getSetting("SIMULATION_RUN_TIME"))
        self.slowRun = int(self.getSetting("RUN_SLOWLY"))
        self.drawSim = int(self.getSetting("DRAW_SIMULATION"))
        self.mask1Prob = float(self.getSetting("MASK_1_INFECTION_PROBABILITY"))
        self.mask2Prob = float(self.getSetting("MASK_2_INFECTION_PROBABILITY"))
        self.mask3Prob = float(self.getSetting("MASK_3_INFECTION_PROBABILITY"))
        self.fracToQuarantine = float(self.getSetting("FRACTION_TO_QUARANTINE"))
        self.daysBeforeQuarantine = int(self.getSetting("DAYS_BEFORE_QUARANTINE"))

        # Initialise Simulation
        self.makeSimulation()

    def makeSimulation(self):
        """
        Runs through methods to create and set up the simulation.
        :return: None
        """
        # Calculate size of the playing field
        sizes = self.calcSimSize()
        self.simSizeX = sizes[0]
        self.simSizeY = sizes[1]

        # Create matrix of Cell objects
        self.makeCellMatrix()

        # Distribute population
        self.distributePopulation()
        print("The city's population is %s" % self.population)

        # Distribute prevention methods
        self.distributePreventionMethods()

        # Calculate initial stats
        self.percentageInfected = self.totInfected / self.population

    def getUserInput(self):
        """
        Asks the user to input things that would be too cumbersome for the settings file or things
        that change with every run.
        :return:
        pos: list(list(int)) = x and y coordinates for initially infected cells.
        inf: list(int) = Fraction of people infected in cell at corresponding coords stored in pos.
        """
        print("Getting user input...")
        pos = []
        inf = []
        choice = "y"
        while choice != "n" or choice != "N":
            choice = input("Add a new infected cell? Y/n: ")
            if choice == "y" or choice == "Y" or choice == "":
                posChoice = input("Input new cell's position (xx, yy): ")
                infChoice = input("Input fraction of people infected: ")
                posSplit = posChoice.split(",")
                pos.append(posSplit)
                inf.append(infChoice)

            elif choice == "n" or choice == "N":
                break
            else:
                print("Invalid input!")
                choice = "y"
                continue
        return pos, inf

    def calcSimSize(self):
        """
        Takes square root of tot area of the simulation to work out the side length. Able to handle non-square fields.
        :return:
        x: int = side length of the simulation in x-direction
        y: int = side length of the simulation in y-direction
        """
        print("Calculating simulation size...")
        uArea = self.uArea
        surrArea = self.surrArea

        totArea = uArea + surrArea
        sideLength = int(sqrt(totArea))

        x = sideLength
        y = sideLength

        print("Simulation size set to %s by %s." % (x, y))
        return x, y

    def distributePopulation(self):
        print("Calculating population distribution...")
        cells = self.cells
        # Urban population
        urbanCells = []
        surrCells = []
        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                cell = cells[y][x]
                if cell.isUrban:
                    urbanCells.append(cell)
                else:
                    surrCells.append(cell)

        urbanPop = self.uPop
        print("Distributing urban population...")
        while urbanPop > 0:
            rand = randint(0, len(urbanCells) - 1)
            cellToIncrease = urbanCells[rand]
            cellToIncrease.population += 10
            self.population += 10
            urbanPop -= 10

        surrPop = self.surrPop
        print("Distributing surrounding population...")
        while surrPop > 0:
            rand = randint(0, len(surrCells) - 1)
            cellToIncrease = surrCells[rand]
            cellToIncrease.population += 10
            self.population += 10
            surrPop -= 10

        print("Calculating infected population...")
        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                cell = cells[y][x]
                cell.infectedPop = int(cell.population * cell.infFraction)
                self.totInfected += cell.infectedPop
                self.totCases += cell.infectedPop

    def distributePreventionMethods(self):
        maskType1Available = int(self.getSetting("AMOUNT_OF_MASKS_TYPE_1"))
        maskType2Available = int(self.getSetting("AMOUNT_OF_MASKS_TYPE_2"))
        maskType3Available = int(self.getSetting("AMOUNT_OF_MASKS_TYPE_3"))

        for type in range(1, 4):
            print("Distributing masks of type %s" % (type))
            if type == 1:
                masksAvailable = maskType1Available
            elif type == 2:
                masksAvailable = maskType2Available
            elif type == 3:
                masksAvailable = maskType3Available
            else:
                raise ValueError

            urbanMasks = int(0.6 * masksAvailable)
            ruralMasks = int(masksAvailable - urbanMasks)

            urbanCells = []
            ruralCells = []

            for y in range(self.simSizeY):
                for x in range(self.simSizeX):
                    cell = self.cells[y][x]
                    if cell.isUrban:
                        urbanCells.append(cell)
                    else:
                        ruralCells.append(cell)

            print("Distributing masks to urban areas...")
            while urbanMasks > 0:
                rand = randint(0, len(urbanCells) - 1)
                cellToIncrease = urbanCells[rand]
                if type == 1:
                    cellToIncrease.amountOfMasksType1 += 10
                elif type == 2:
                    cellToIncrease.amountOfMasksType2 += 10
                elif type == 3:
                    cellToIncrease.amountOfMasksType3 += 10
                else:
                    raise ValueError
                urbanMasks -= 10

            print("Distributing masks to surrounding areas...")
            while ruralMasks > 0:
                rand = randint(0, len(ruralCells) - 1)
                cellToIncrease = ruralCells[rand]
                if type == 1:
                    cellToIncrease.amountOfMasksType1 += 10
                elif type == 2:
                    cellToIncrease.amountOfMasksType2 += 10
                elif type == 3:
                    cellToIncrease.amountOfMasksType3 += 10
                else:
                    raise ValueError
                ruralMasks -= 10

    def makeCellMatrix(self):
        print("Creating city cells...")
        # Get inputs from user
        userInput = self.getUserInput()
        posArray = userInput[0]
        infArray = userInput[1]

        cellsRow = []
        cells = []
        count = 0

        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                try:
                    if (x == int(posArray[count][0])) and (y == int(posArray[count][1])):
                        cell = self.makeCell(x, y, infArray[count], self.simSettings)
                        cell.isInfected = True
                        count += 1
                        cellsRow.append(cell)
                    else:
                        cell = self.makeCell(x, y, 0, self.simSettings)
                        cellsRow.append(cell)
                except IndexError:
                    cell = self.makeCell(x, y, 0, self.simSettings)
                    cellsRow.append(cell)
            cells.append(cellsRow)
            cellsRow = []
        self.cells = cells

    def drawSimulation(self, graphics, initialise):
        cells = self.cells
        drawSetting = self.graphMode
        uPop = self.uPop
        surrPop = self.surrPop
        maxPop = ((uPop + surrPop) / (self.simSizeX * self.simSizeY)) * 5
        if initialise:
            print("Drawing cells...")
            for y in range(self.simSizeY):
                for x in range(self.simSizeX):
                    cell = cells[y][x]

                    if cell.isUrban:
                        cell.setOutline("Black")
                    else:
                        cell.setOutline("White")

                    if drawSetting == 0:
                        colVariable = cell.infFraction * 255
                    elif drawSetting == 1:
                        colVariable = (cell.population / maxPop) * 255
                    else:
                        print("Draw setting invalid, fall back to infection drawing.")
                        colVariable = cell.infFraction * 255

                    red = 255
                    green = int(255 - colVariable)
                    blue = int(255 - colVariable)
                    colour = color_rgb(red, green, blue)
                    cell.setFill(colour)
                    cell.draw(graphics)
        else:
            print("Updating cells...")
            for y in range(self.simSizeY):
                for x in range(self.simSizeX):
                    cell = cells[y][x]
                    if drawSetting == 0:
                        colVariable = cell.infFraction * 255
                    elif drawSetting == 1:
                        colVariable = (cell.population / maxPop) * 255
                    else:
                        print("Draw setting invalid, fall back to infection drawing.")
                        colVariable = cell.infFraction * 255

                    red = 255
                    green = int(255 - colVariable)
                    blue = int(255 - colVariable)
                    colour = color_rgb(red, green, blue)
                    cell.setFill(colour)

    def makeCell(self, x, y, infectionFraction, settings):
        c = self.coordScale
        p1 = Point(x * c, y * c)
        p2 = Point((x * c) + c, (y * c) + c)
        newCell = Cell(p1, p2, infectionFraction, settings, [self.simSizeX, self.simSizeY])
        print("New cell at %s, %s created with infection fraction of %s" % (x, y, infectionFraction))

        return newCell

    def getSetting(self, setting):
        value = self.simSettings[self.simSettings.index(setting) + 1]

        return value

    def stepTime(self, t):
        print("Simulating day %s..." % t)
        writeToFile = self.createFile
        cells = self.cells
        newCells = copy.deepcopy(cells)
        self.newRecovered = 0
        self.newInfected = 0
        self.newDead = 0

        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                cell = cells[y][x]
                self.spreadDisease(cell, newCells, x, y, t)

        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                cell = cells[y][x]
                self.killDisease(cell, x, y, t)

        for y in range(self.simSizeY):
            for x in range(self.simSizeX):
                cell = newCells[y][x]
                self.updateCellData(cell, x, y)

        self.cells.clear()
        self.cells = copy.deepcopy(newCells)

        self.calcStats()

        if writeToFile == 1:
            self.writeStats(t)
        print("Day = %s, Current Population = %s, Total Infection Cases = %s, Currently Infected = %s, Percentage "
              "Currently Infected = %s, New Infected Today = %s, Total Dead = %s, New Dead Today = %s, "
              "Total Recovered = %s, New Recovered Today = %s" % (t, self.population, self.totCases,
                                                                  self.totInfected, self.percentageInfected,
                                                                  self.newInfected, self.totDead, self.newDead,
                                                                  self.totRecovered, self.newRecovered))

    def spreadDisease(self, cell, newCells, x, y, t):
        print("Spreading disease on cell at %s, %s..." % (x, y), end="\r")
        growthFactor = random.uniform(0, self.spreadRate)

        if t > self.daysBeforeQuarantine:
            newPplInfected = int(((cell.population * cell.infFraction) * (1 - self.fracToQuarantine)) * growthFactor)
        else:
            newPplInfected = int(cell.population * cell.infFraction * growthFactor)

        if cell.amountOfMasksType1 != 0:
            newPplInfected -= newPplInfected * (cell.amountOfMasksType1 / cell.population) * (1 - self.mask1Prob)
            newPplInfected = int(newPplInfected)
        elif cell.amountOfMasksType2 != 0:
            newPplInfected -= newPplInfected * (cell.amountOfMasksType2 / cell.population) * (1 - self.mask2Prob)
            newPplInfected = int(newPplInfected)
        elif cell.amountOfMasksType3 != 0:
            newPplInfected -= newPplInfected * (cell.amountOfMasksType3 / cell.population) * (1 - self.mask3Prob)
            newPplInfected = int(newPplInfected)
        else:
            pass

        checkNewPplInfected = newPplInfected
        quotient = 1
        power = - 1
        while quotient != 0:
            quotient = int(checkNewPplInfected / 10)
            checkNewPplInfected = quotient
            power += 1

        amountOfPeopleToAdd = int(10 ** (power - 1))
        if power - 1 < 0:
            amountOfPeopleToAdd = 1

        for i in range(0, newPplInfected, amountOfPeopleToAdd):
            randX = randint(-1, 1)
            randY = randint(-1, 1)
            newInfectedAdded = amountOfPeopleToAdd

            try:
                if x + randX == -1 or y + randY == -1:
                    raise IndexError

                editedCell = newCells[y + randY][x + randX]

                if newInfectedAdded + editedCell.infectedPop > editedCell.population:
                    newInfectedAdded = abs(editedCell.population - editedCell.infectedPop)
                    editedCell.infectedPop += newInfectedAdded
                    self.newInfected += newInfectedAdded
                else:
                    editedCell.infectedPop += newInfectedAdded
                    self.newInfected += newInfectedAdded

                try:
                    editedCell.infFraction = round(editedCell.infectedPop / editedCell.population, 4)
                except ZeroDivisionError:
                    editedCell.infFraction = 0

            except IndexError:
                editedCell = newCells[y][x]
                newInfectedAdded = amountOfPeopleToAdd

                if newInfectedAdded + editedCell.infectedPop > editedCell.population:
                    newInfectedAdded = abs(editedCell.population - editedCell.infectedPop)
                    editedCell.infectedPop += newInfectedAdded
                    self.newInfected += newInfectedAdded
                else:
                    editedCell.infectedPop += newInfectedAdded
                    self.newInfected += newInfectedAdded

                try:
                    editedCell.infFraction = round(editedCell.infectedPop / editedCell.population, 4)
                except ZeroDivisionError:
                    editedCell.infFraction = 0

    def updateCellData(self, cell, x, y):
        print("Updating cell data for cell at %s, %s..." % (x, y), end="\r")
        if cell.isInfected:
            cell.age += 1
        elif not cell.isInfected and cell.infectedPop != 0:
            cell.isInfected = True
        elif not cell.isInfected and cell.infectedPop == 0:
            cell.isInfected = False
            cell.age = 0

    def killDisease(self, cell, x, y, t):
        print("Calculating reduction of disease at %s, %s..." % (x, y), end="\r")
        minIncPeriod = self.minIncubation
        maxIncPeriod = self.maxIncubation
        recTime = self.recTime
        deathRate = self.deathRate
        recRate = self.recRate
        reductionRate = self.reductionRate
        diseaseLifetime = randint(minIncPeriod, maxIncPeriod + recTime)

        if t >= diseaseLifetime:
            reductionInInfectedPop = cell.infectedPop * random.uniform(0, reductionRate)
            cell.infectedPop -= reductionInInfectedPop
            if cell.infectedPop < 0:
                reductionInInfectedPop = cell.infectedPop
                cell.infectedPop = 0

            deaths = int(reductionInInfectedPop * deathRate)
            self.newDead += deaths
            recoveries = int(reductionInInfectedPop * recRate)
            self.newRecovered += recoveries

            cell.population -= deaths
            if cell.population < 0:
                cell.population = 0

            try:
                cell.infFraction = round(cell.infectedPop / cell.population, 4)
            except ZeroDivisionError:
                cell.infFraction = 0
        else:
            pass

    def calcStats(self):
        self.population -= self.newDead
        self.totCases += self.newInfected
        self.totInfected += (self.newInfected - self.newDead)
        self.totDead += self.newDead
        self.totRecovered += self.newRecovered
        self.percentageInfected = round(100 * self.totInfected / self.population, 4)

    def writeStats(self, t):
        data = [t, self.population, self.totCases, self.totInfected, self.percentageInfected, self.newInfected,
                self.totDead, self.newDead, self.totRecovered, self.newRecovered]
        with open("data.csv", "a", newline="") as dataFile:
            csvWrite = csv.writer(dataFile)
            csvWrite.writerow(data)

    def runSimulation(self):
        runTime = self.runTime
        slowRun = self.slowRun
        coordScaling = self.coordScale
        drawSim = self.drawSim
        writeFile = self.createFile
        win = False

        if slowRun == 1:
            input("Press enter to continue.")
            pass

        if writeFile == 1:
            header = ["Day", "Current Population", "Total Infection Cases", "Currently Infected",
                      "Percentage Currently Infected", "New Infected Today", "Total Dead", "New Dead Today",
                      "Total Recovered", "New Recovered Today"]
            with open("data.csv", "w", newline="") as dataFile:
                csvWrite = csv.writer(dataFile)
                csvWrite.writerow(header)

        if drawSim == 1:
            win = GraphWin("Coronavirus", self.simSizeX * coordScaling, self.simSizeY * coordScaling)

        for t in range(runTime):
            if t == 0 and drawSim:
                self.drawSimulation(win, initialise=True)
            elif t != 0 and drawSim:
                self.drawSimulation(win, initialise=False)
            self.stepTime(t)
            if slowRun:
                input("Press enter to continue.")
                continue
