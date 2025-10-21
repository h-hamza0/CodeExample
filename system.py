# Input: Molecules Class\
# Output: .gro files/.top files/System Class\

# Purpose: Consolidate molecules to simulation box. This is a dynamic class, with it's .gro reference changing after each system run and .top changing whilst developing the simulation box
# runs act on a system

from molecules import *
import sys
from runBlock import *
from gmxCommands import *
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from BoxManager import *
from CoarseGrainConverter import *
from DirectoryManager import *
from IndexManager import *
from MoleculeManager import *
from TopologyManager import *

@dataclass
class SystemConfig: # can probably just keep for now, will look later in to how to remove this. 
    gmx_run: str
    gmx_path: Path
    input_dir: Path
    output_dir: Path
    idx_groups: list
    box_size: float
    box_dist: float
    wradius: float
    cg2at: bool
    us_path: Optional[Path] = None

@dataclass
class SystemState: # will need to be called outside this though.
    current_file: Optional[Path] = None


class System:
    def __init__(self, gmx_run, gmx_path, input_dir, output_dir, forcefield, idxGRPS, boxSize, boxDist, Wradius, cg2at, US="None") -> None: 
        self.molecules = list()
        self.runs = list()
        self.gmx_run = gmx_run
        self.gmx_path = gmx_path
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.forcefield = Path(forcefield)
        self.topology = None
        self.updatedFile = None
        self.idxGRPS = idxGRPS
        self.boxSize = boxSize
        self.boxDist = boxDist
        self.Wradius = Wradius
        self.cg2at = cg2at
        self.indx = None
        self.US = US
        self.updatedTraj = None
        self.updatedTPR = None
        self.cg2atPath = None
        self.BoxManager = None
        self.CoarseGrainConverter = None
        self.IndexManager = None
        self.DirectoryManager = None
        self.MoleculeManager = None
        self.SystemManager = None
        self.TopologyManager = None
    
    def addRuns(self, s: Run) -> None:
        self.runs.append(s)
        return None
    
    def updateLatestFile(self, s) -> None:
        if len(s) == 1:
            self.updatedFile = s[0]
        else:
            self.updatedFile = s[0]
            self.trajectory = s[1]
            self.prevTPR = s[2]
        return None
    
    def retrieveStatus(self) -> None: # simply logging, can be replaced
        print(f'Molecules: {self.molecules}')
        print(f'Stages: {self.runs}')
        return None
    
    def prepRun(self) -> None:
        self.BoxManager = BoxManager(self)
        self.CoarseGrainConverter = CoarsegrainConvert(self)
        self.DirectoryManager = DirectoryManager(self)
        self.IndexManager = IndexManager(self)
        self.MoleculeManager = MoleculeManager(self)
        self.TopologyManager = TopologyManager(self)

    def setup(self) -> None: # stays here
        self.prepRun()
        self.DirectoryManager.checkExistence() # ignore error, works just fine
        if self.cg2at != 'False':
            self.CoarseGrainConverter.cgConvert()
        self.DirectoryManager.setupDirectory()
        self.MoleculeManager.manage()
        if int(self.boxDist) != 0:
            self.BoxManager.centerBox()
        if self.cg2at != 'False':
            self.BoxManager.solvateAA()
            self.BoxManager.ionizeBox()
        else:
            self.BoxManager.solvateBox()
        self.IndexManager.generateIndex()
        return None



