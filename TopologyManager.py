from gmxCommands import *

class TopologyManager:
    def __init__(self, system) -> None:
        self.system = system

    def generateTopology(self):
        # itp directives, positional restraints, system name, molecules
        topology = ""

        # force field inclusion
        for f in sorted(self.system.forcefield.iterdir()):
            if f.suffix == '.itp':
                if f.name == 'forcefield.itp' or ('martini' in f.name):
                    topology += f'#include <{f.absolute()}>\n'
                if f.name == 'ions.itp' or f.name == 'tip3p.itp':
                    topology += f'#include <{f.absolute()}>\n'
                #else:
                #    topology += f'#include <{f.absolute()}>\n'
        # itp directives
        for m in self.system.MoleculeManager.molecules:
            m = self.system.MoleculeManager.getMolecule(m)
            if m.itp_file != None:
                topology += f"#include <{m.itp_file}>\n"

        topology += f' [ system ] \nSystem\n [ molecules ]\n'


        for m in self.system.MoleculeManager.molecules:
            m = self.system.MoleculeManager.getMolecule(m)
            topology += f"{m.name}   {m.nmol}\n"

        self.system.topology = Path(self.system.output_dir / self.system.name / 'setup' / 'topol.top')

        with open(self.system.topology, 'w') as f:
            f.writelines(topology)
        
        return None