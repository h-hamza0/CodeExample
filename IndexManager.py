from gmxCommands import *

class IndexManager:
    def __init__(self, system) -> None: 
        self.system = system

    def generateIndex(self) -> None:
        indx = Path(self.system.output_dir) / 'setup' / 'index.ndx'
        self.system.indx = indx.absolute()
        makeIndex(self.system.SystemManager.latestFile[0], indx.absolute(), self.system.idxGRPS)
        return None
