# Manages all molecule(s) operations
from molecules import *
from gmxCommands import *
import shutil
class MoleculeManager:
    def __init__(self, system) -> None:
        self.molecules = list()
        self.system = system

    def updateMoleculeStorage(self, m:Molecule) -> None:
        self.molecules.append(m)
        return None
    
    def setITP(self) -> None:
        """
        Copy ITP from root directory into simulation folder (mand.)
        """
        for m in self.molecules: # self.system.input_dir / output_dir will have to be handled in a more efficient way though, how do we interface with it?
            cgP = Path(self.system.input_dir) / 'CG' / f'{m.name}.itp' 
            aaP = Path(self.system.input_dir) / 'AA' / f'{m.name}.itp' 
            if m.CGAT == 'True':
                dest = Path(self.system.output_dir) / 'setup' / 'CG' / 'itp' / f'{m.name}.itp' # both CG and AA itp directories will have to be made
                shutil.copy(cgP.absolute(), dest.absolute())
                m.updateITP(dest)
            else:
                dest = Path(self.system.output_dir) / 'setup' / 'AA' / 'itp' / f'{m.name}.itp'
                shutil.copy(aaP.absolute(), dest.absolute())
                m.updateITP(dest)

    def setGRO(self) -> None:
        """
        Copy over GRO from root directory into simulation folder (if avail.)
        """
        for m in self.molecules:
            cgP = Path(self.system.input_dir) / 'CG' / f'{m.name}.gro' 
            aaP = Path(self.system.input_dir) / 'AA' / f'{m.name}.gro' 
            if m.CGAT == 'True':
                dest = Path(self.system.output_dir) / 'setup' / 'molecules' / 'CG' / f'{m.name}.gro'
                shutil.copy(cgP.absolute(), dest.absolute())
                m.updateGRO(dest)
            else:
                if aaP.exists():
                    dest = Path(self.system.output_dir) / 'setup' / 'molecules' / 'AA' / f'{m.name}.gro'
                    shutil.copy(aaP.absolute(), dest.absolute())
                    m.updateGRO(dest)
                    m.computePDB()
                else:
                    m.updateGRO('UNAVAIL')

    def insertMolecules(self) -> None: # alot cleaner and easier to look at.
        for m in self.molecules:
            if m.insert == 'True' and m.packmol == 'False':
                output = Path(self.system.output_dir / 'setup' / f'{m.name}_boxed.gro').absolute()
                insert_molecules(m.gro_file, output, self.system.boxSize, m.nmol, m.insertion_radius, self.system.updatedFile) # interface
                self.system.updatedFile = output
            else:
                output = Path(self.system.output_dir / 'setup' / f'{m.name}_boxed.pdb').absolute()
                packMol(self.system.updatedFile, m.pdb_file, output, 100, self.system.output_dir)
                center_setup(output, output, self.system.boxSize)
                self.updatedFile = output
        
        return None
    
    def manage(self) -> None:
        self.setITP()
        self.setGRO()
        self.insertMolecules()

