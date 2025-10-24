from gmxCommands import *

class CoarsegrainConvert:
    def __init__(self, system) -> None:
        self.system = system

    def cgConvert(self) -> None:
        destination = Path(self.system.output_dir / 'CG')
        finalLoc = cg2atConvert(self.system.SystemManager.latestFile[0], destination)
        self.system.cg2atPath = finalLoc
        self.system.SystemManager.latestFile = [finalLoc]
        return None
