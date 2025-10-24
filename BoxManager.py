from gmxCommands import *
from collections import Counter
import MDAnalysis as mda

class BoxManager:
    def __init__(self, system) -> None:
        self.system = system

    def centerBox(self) -> None:
        output = Path(self.system.output_dir / self.system.name /'setup' / 'centered.gro').absolute()
        print(self.system.SystemManager.latestFile[0])
        center_setup(self.system.SystemManager.latestFile[0], output, [int(self.system.boxDist)] * 3)
        self.system.SystemManager.latestFile = [output]
        return None
    
    def solvateBox(self) -> None:
        output = Path(self.system.output_dir / self.system.name /'setup' / 'solvated.gro').absolute()
        solvate(self.system.SystemManager.latestFile[0], Path(self.system.output_dir / self.system.name/'setup' / 'molecules' /'water.gro').absolute(), output, self.system.Wradius)
        self.system.SystemManager.latestFile = [output]
        return None
    
    def solvateAA(self) -> None:
        output = Path(self.system.SystemManager.latestFile[0] / 'setup' / 'solvated.gro').absolute()
        solvAA(self.system.SystemManager.latestFile[0], 'spc216', output)
        self.system.SystemManager.latestFile = [output]
        return None
    
    def ionizeBox(self) -> None:
        output = Path(self.system.output_dir / self.system.name / 'setup' / 'ionized.gro').absolute()
        ionsMDP = Path("/Users/hamzahabib/Desktop/HaoLab/workingCode/lib/baseScripts/ions.mdp") # better way to do this?
        ionsTpr = Path(self.system.output_dir / self.system.name / 'setup' / 'ions.tpr')
        ionize(self.system.SystemManager.latestFile[0], ionsTpr, output, ionsMDP, self.system.topology)
        self.system.SystemManager.latestFile = [output] # use better set methods... unsafe rn.
        return None

    def computeComponents(self) -> None:
        file = self.system.SystemManager.latestFile[0]
        u = mda.Universe(file)
        resnames = [res.resname for res in u.residues]
        counts = Counter(resnames)
        for name, count in counts.items():
            self.system.MoleculeManager.updateMoleculeCount(name, count)