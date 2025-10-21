from gmxCommands import *

class BoxManager:
    def __init__(self, system) -> None:
        self.system = system

    def centerBox(self) -> None:
        output = Path(self.system.output_dir / 'setup' / 'centered.gro').absolute()
        center_setup(self.system.updatedFile, output, [int(self.system.boxDist)] * 3)
        self.system.updatedFile = output
        return None
    
    def solvateBox(self) -> None:
        output = Path(self.system.output_dir / 'setup' / 'solvated.gro').absolute()
        #  Path(self.output_dir / 'setup' / 'molecules' / 'water.gro').absolute()
        solvate(self.system.updatedFile, Path(self.system.output_dir / 'setup' / 'molecules' / 'water.gro').absolute(), self.system.topology, output, self.system.Wradius)
        self.system.updatedFile = output
        return None
    
    def solvateAA(self) -> None:
        output = Path(self.system.output_dir / 'setup' / 'solvated.gro').absolute()
        solvAA(self.system.updatedFile, 'spc216', self.system.topology, output)
        self.system.updatedFile = output
        return None
    
    def ionizeBox(self) -> None:
        output = Path(self.system.output_dir / 'setup' / 'ionized.gro').absolute()
        ionsMDP = Path("/zfshomes/hpc15/SummerWork/BileSaltProject/lib/baseScripts/ions.mdp") # better way to do this?
        ionsTpr = Path(self.system.output_dir / 'setup' / 'ions.tpr')
        ionize(self.system.updatedFile, ionsTpr, output, ionsMDP, self.system.topology)
        self.system.updatedFile = output
        return None
