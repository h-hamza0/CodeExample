# Responsbile for stitching together multiple systems, additionally, utilization of a single, transient upkeep file
from gmxCommands import *
class SystemManager:
    def __init__(self) -> None:
        self.systems = list()
        self.latestFile = None

    def addSystem(self, s):
        self.systems.append(s)

    def run(self): # will most likely be our entry point.
        for sys in self.systems:
            sys.latestFile = self.latestFile # bridge between systems.
            sys.run()
            self.latestFile = sys.retrieveLatest()

    