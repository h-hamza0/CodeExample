# Manages all molecule(s) operations
from molecules import *
from gmxCommands import *
import shutil
class MoleculeManager:
    def __init__(self, system) -> None:
        self.molecules = dict()
        self.system = system

    def updateMoleculeStorage(self, m:Molecule) -> None:
        self.molecules[m.name] = m
        return None
    
    def updateMoleculeCount(self, m:str, c:int) -> None:
        self.molecules[m].nmol = c
        return None
    
    def getMolecule(self, m:str) -> Molecule:
        return self.molecules[m]
    
    def setITP(self) -> None:
        """
        Copy ITP from root directory into simulation folder (mand.)
        """
        for m in self.molecules: # self.system.input_dir / output_dir will have to be handled in a more efficient way though, how do we interface with it?
            m = self.molecules[m]
            if m.itp == 'True':
                if m.CGAT == 'True':
                    cgP = Path(self.system.input_dir) / 'CG' / f'{m.name}.itp' 
                    dest = Path(self.system.output_dir) / 'setup' / 'CG' / 'itp' / f'{m.name}.itp' # both CG and AA itp directories will have to be made
                    dest.parent.mkdir(parents=True, exist_ok=True)  
                    shutil.copy(cgP.absolute(), dest.absolute())
                    m.updateITP(dest)
                else:
                    aaP = Path(self.system.input_dir) / 'AA' / f'{m.name}.itp' 
                    dest = Path(self.system.output_dir) / 'setup' / 'AA' / 'itp' / f'{m.name}.itp'
                    dest.parent.mkdir(parents=True, exist_ok=True)  
                    shutil.copy(aaP.absolute(), dest.absolute())
                    m.updateITP(dest)

    def setGRO(self) -> None:
        """
        Copy over GRO from root directory into simulation folder (if avail.)
        """
        for m in self.molecules:
            m = self.molecules[m]
            if m.itp == 'True':
                if m.CGAT == 'True':
                    cgP = Path(self.system.input_dir) / 'CG' / f'{m.name}.gro' 
                    dest = Path(self.system.output_dir) / 'setup' / 'molecules' / 'CG' / f'{m.name}.gro'
                    dest.parent.mkdir(parents=True, exist_ok=True)  
                    shutil.copy(cgP.absolute(), dest.absolute())
                    m.updateGRO(dest)
                else:
                    aaP = Path(self.system.input_dir) / 'AA' / f'{m.name}.gro' 
                    if aaP.exists():
                        dest = Path(self.system.output_dir) / 'setup' / 'molecules' / 'AA' / f'{m.name}.gro'
                        dest.parent.mkdir(parents=True, exist_ok=True)  
                        shutil.copy(aaP.absolute(), dest.absolute())
                        m.updateGRO(dest)
                        m.computePDB()
                    else:
                        m.updateGRO('UNAVAIL')

    def insertMolecules(self) -> None: # alot cleaner and easier to look at.
        for m in self.molecules:
            m = self.molecules[m]
            if m.insert == 'True' and m.packmol == 'False':
                output = Path(self.system.output_dir / 'setup' / f'{m.name}_boxed.gro').absolute()
                insert_molecules(m.gro_file, output, self.system.boxSize, m.nmol, m.insertion_radius, self.system.SystemManager.latestFile[0]) # interface
                self.system.SystemManager.latestFile = [output]
            elif m.packmol == 'True':
                output = Path(self.system.output_dir / 'setup' / f'{m.name}_boxed.pdb').absolute()
                packMol(self.system.SystemManager.latestFile[0], m.pdb_file, output, 100, self.system.output_dir)
                center_setup(output, output, self.system.boxSize)
                self.system.SystemManager.latestFile = [output]
        
        return None
    
    def manage(self) -> None:
        self.setITP()
        self.setGRO()
        self.insertMolecules()

