# Input: System Class\
# Output: .gro files\
# Purpose: Serves as an interface to the System class for developing the pipeline and handles execution of 'gmx'
from pathlib import Path
from molecules import *
from runBlock import *
from system import *
from SystemManager import *
from typing import Union
import ast
import sys

# also look into error logging

class Parser: 
    """
    Input: .txt file
    Object of this block of code is to read in text input and to convert it to appropriate blocks
    """
    def __init__(self, fname) -> None:
        self.path = Path(fname) 
        self.molecules = list()
        self.runs = list()
        self.systems = SystemManager()

    def listToDict(self, list:list) -> dict:
        """
        Given [k=v, k=v, ...] -> {k:v, ...}
        """
        base = dict() 
        for e in list:
            k, v = e.split('=')
            k = k.strip()
            v = v.strip()
            if k == 'idxGRPS':
                idx = []
                for grp in v.split(' '):
                    idx.append({grp.split(':')[0]:ast.literal_eval(grp.split(':')[1])})
                base[k] = idx
            elif len(v.split(' ')) > 1 and '{' not in v:
                base[k] = v.split(' ')
            else:
                base[k] = v
        return base

    # check method to ensure file accuracy
    def check(self) -> None:
        with open(self.path, 'r') as f:
            lines = f.readlines()[::-1] 
        lines = [x.strip() for x in lines if x != '\n']
        while len(lines) > 0:
            cond = lines.pop()
            vals = list()
            if cond == 'sys':
                while lines[-1] != 'end':
                    vals.append(lines.pop())
                if len(vals) != 0:
                    self.checkSystem(vals)
                else:
                    raise NotImplementedError
            elif cond.split('_')[0] == 'molecule':
                while lines[-1] != 'end':
                    vals.append(lines.pop())
                if len(vals) != 0:
                    self.checkMolecule(vals)
                else:
                    raise NotImplementedError
            elif cond.split('_')[0] == 'stage':
                while lines[-1] != 'end':
                    vals.append(lines.pop())
                if len(vals) != 0:
                    self.checkRun(vals)
                else:
                    raise NotImplementedError
            elif cond == 'end':
                continue
            else:
                raise NotImplementedError
        return None
    
    def checkMolecule(self, lines:list) -> None:
        """
        Required Parameters:
        nmol = int
        insertion_radius = float
        """
        p = self.listToDict(lines)
        print(f'Parsing: Molecule {p["name"]}')
        requiredParams = ['nmol', 'insertion_radius', 'CGAT']
        for r in requiredParams:
            if r not in p:
                print(f"Missing {r}!")
                raise NotImplementedError
        self.molecules.append(self.developMolecule(**p)) # instead of passing to self.molecules, pass to MoleculeManager.
        
        return None
    
    def checkSystem(self, lines:list) -> None:
        """
        Required Parameters:
        gmx_run = bool
        gmx_path = fname [ if gmx_run = True ]
        input_dir = fname [ also check existance ]
        output_dir = fname [ check existance | if not then make ]
        forcefield = str
        """
        p = self.listToDict(lines)
        print(f'Parsing: System')
        requiredParams = ['name', 'gmx_run', 'gmx_path', 'input_dir', 'output_dir', 'forcefield', 'idxGRPS', 'boxSize', 'boxDist', 'Wradius', 'US', 'cg2at', 'resolvate']

        for r in requiredParams:
            if r not in p:
                print(f"Missing {r}!")
        system = self.developSystem(**p) # instead of passing to self.system, pass to SystemManager.
        self.systems.addSystem(system)
        if not Path(p['input_dir']).is_dir():
            print('Input Directory does not exist')
            raise NotADirectoryError
        return None
    
    def checkRun(self, lines:list) -> None:
        """
        Required Parameters:
        type = str
        """
        p = self.listToDict(lines)
        print(f'Parsing: Stage {p["type"]}')
        requiredParams = ['type']
        for r in requiredParams:
            if r not in p:
                print(f"Missing {r}!")
                raise NotImplementedError
        self.runs.append(self.developRun(**p))
        return None
    
    def developSystem(self, **kwargs) -> System:
        return System(**kwargs)
    
    def developMolecule(self, **kwargs) -> Molecule:
        return Molecule(**kwargs) # read into best way to properly handle these arguments, most likely dictionary associations
    
    def developRun(self, **kwargs) -> Run:
        return Run(**kwargs)

    def parse(self) -> SystemManager: # Physical representation of pipeline all HeadController would do is for each step in pL, run step, perform validations, proceed with next steps. Fancy for loop
        self.check()
        for m in self.molecules:
            self.systems.retrieveSystem(m.system).MoleculeManager.updateMoleculeStorage(m)
        for s in self.runs:
            self.systems.retrieveSystem(s.system).addRuns(s)
        return self.systems # instance of SystemManager.

p = Parser(f"{sys.argv[1]}")
systems = p.parse()
systems.run()
