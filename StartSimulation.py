import csv
from Data.Simulation import *

settings = []
with open("SimulationSettings.csv", "r") as settingsFile:
    rows = csv.reader(settingsFile, delimiter="=")
    for row in rows:
        try:
            if list(row[0])[0] == "#":
                continue
            else:
                settings += row
        except IndexError:
            continue
print("Simulation settings loaded from file.")

print("Creating Simulation...")
simulation = Simulation(settings)
print("Simulation created!")
print("Starting simulation...")
simulation.runSimulation()
input("Simulation finished, press enter to exit")
quit()
