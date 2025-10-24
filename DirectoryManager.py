# Responsible for moving/copying files, making sure all is in order
from gmxCommands import *
import shutil
class DirectoryManager:
    def __init__(self, system) -> None:
        self.system = system

    def checkExistence(self) -> None:
        if Path(self.system.output_dir / self.system.name).exists():
            print('Directory Already Exists | Continuations are not yet supported, ending run... ')
            shutil.rmtree(Path(self.system.output_dir / self.system.name).absolute())
            print('Fresh Start')
        Path(self.system.output_dir / self.system.name).mkdir()
        return None
    
    def setupDirectory(self) -> None:
        """
        Responsible for setting up directory
        """
        Path(self.system.output_dir / f'{self.system.name}' / 'setup').mkdir()
        Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'molecules').mkdir() # where .gro lives
        Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'itp').mkdir() # where .itp lives
        Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'forcefield').mkdir() # where ff lives
        # Copy forcefield here automatically
        shutil.copytree(self.system.forcefield, Path(self.system.output_dir / f'{self.system.name}' / "setup" / "forcefield"), dirs_exist_ok=True)
        self.system.forcefield = Path(self.system.output_dir / f'{self.system.name}' / "setup" / "forcefield")

        # copy Water
        src = Path(self.system.input_dir / 'water.gro') # these sorts of copy can be pushed into another library
        dest = Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'molecules' / 'water.gro')
        shutil.copy(src, dest)

        if self.system.US != "None": # old directory
            # copy topology and update topology path # all we need to do then is to remove 
            src = Path(self.system.US) / 'setup' / 'topol.top'
            dest = Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'topol.top') 
            shutil.copy(src, dest)

            # copy aligned system
            src = Path(self.system.US) / 'MD' / 'clust.gro'
            dest = Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'clust.gro')
            shutil.copy(src, dest)
            minim = Path(self.system.output_dir / f'{self.system.name}' / 'setup' / 'minimum.pdb')
            minimal_setup(dest.absolute(), minim.absolute(), 0)
            self.system.SystemManager.latestFile = [minim]
            # if self.system.cg2at == 'True':
            #     self.system.SystemManager.latestFile = self.system.cg2atPath
        return None
