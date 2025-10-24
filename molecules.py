# Input: .itp/.gro files\
# Output: Molecules Class\

# Purpose: Streamline implementation of Molecules into a system
from pathlib import Path
import subprocess
# [More to be added]

class Molecule:
    def __init__(self, name, system, nmol, insertion_radius, CGAT, packmol, insert, itp) -> None: # also pass this hthrough a data class...
        self.name = name
        self.system = system
        self.itp_file = None
        self.gro_file = None
        self.nmol = int(nmol)
        self.insertion_radius = insertion_radius
        self.beadN = None
        self.packmol = packmol
        self.pdb_file = None
        self.CGAT = CGAT
        self.itp = itp
        self.insert = insert # decide if we are actually inserting this into the system or just using it to make our topology
    # Base molecule class, params such as name, itp file, gro file [ itp and gro added in system parse and setup ]

    # what else should I add?
    def updateITP(self, m) -> None:
        # setting itp file # should the distinction be added here? for cg/aa?
        self.itp_file = m
        return None
    
    def updateGRO(self, m) -> None:
        # setting gro file
        self.gro_file = m
        return None
    def setBeadN(self) -> None:
        with open(self.gro_file, 'r') as f:
            ls = f.readlines()
        self.beadN = len(ls) - 3
    def computePDB(self) -> None:
        # gmx run for conversion
        root = self.gro_file.parent
        self.pdb_file = Path(f'{root}/{self.name}.pdb').absolute()
        subprocess.run(['gmx', 'editconf', '-f', self.gro_file, '-o', self.pdb_file])
        return None



