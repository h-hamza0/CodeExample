from gmxCommands import *
from system import *
from collections import OrderedDict
class SystemManager:
    def __init__(self) -> None:
        self.systems = OrderedDict()
        self.latestFile = None

    def addSystem(self, s) -> None:
        self.systems[s.name] = s
        self.systems[s.name].SystemManager = self
        if s.US != 'None': 
            self.latestFile = [Path(s.US) / 'MD' / 'clust.gro']
        return None
    
    def retrieveSystem(self, s) -> System:
        return self.systems[s]

    def run(self) -> None:
        for sys in self.systems:
            self.systems[sys].setup()
            for r in self.retrieveSystem(sys).runs:
                r.run()
                self.latestFile = r.retrieveLatestFile()
    