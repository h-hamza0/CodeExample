from gmxCommands import *

class CoarsegrainConvert:
    def __init__(self, system) -> None:
        self.system = system

    def cgConvert(self) -> None:
        destination = Path(self.system.output_dir / 'CG')
        finalLoc = cg2atConvert(Path(self.system.US) / 'MD' / 'clust.gro', destination)
        self.system.cg2atPath = finalLoc
        self.system.updatedFile = finalLoc
        return None
