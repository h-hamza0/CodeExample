# This would house the system and associated mdp file, would output gmx commands
from pathlib import Path
from gmxCommands import *
import shutil
from typing import Union
import numpy as np
import MDAnalysis as mda
from MDAnalysis.core.groups import AtomGroup
from numpy.linalg import norm
import os

class Run:
    def __init__(self, type, system, **additional) -> None:
        self.type = type
        self.system = system
        self.additional = additional # additional stores information which the user has put in
        self.mdpFile = Path()  # we can have a base MDP file, 
        self.mdpArguments = dict()
        self.outLocation = Path()
        self.indexF = None
        self.center = None
        self.US = True if self.additional.get('US') != None else False
        self.configNames = list()
        self.trajectory = None
        self.prevTPR = None

    def updateOutLocation(self, p) -> None:
        if Path(p).exists():
            shutil.rmtree(p)
        Path.mkdir(p)
        self.outLocation = p
        return None
    
    def updateUpdatedFile(self, p: str) -> None:
        if len(p) == 1:
            self.updatedFile = p[0]
        else:
            self.updatedFile = p[0]
            self.trajectory = p[1]
            self.prevTPR = p[2]
        return None
    
    def updateIndex(self, p: str) -> None:
        self.indexF = p
        return None

    def parseMDP(self) -> None:
        # option to set MDP 
        if self.mdpFile != None:
            self.mdpArguments = dict()
            with open(self.mdpFile, 'r') as f:
                lines = f.readlines()
            for l in lines:
                l = l.strip()
                if l != '' and ';' not in l:
                    args = l.split('=')
                    # extraction of information
                    da = args[1].split(';')[0].split()
                    self.mdpArguments[args[0].strip()] = da
        else:
            print('Requested MDP File does not exist!')
        
    def updateMDP(self) -> None:
        # takes additional and writes 
        for arg in self.additional:
            self.mdpArguments[arg] = self.additional[arg]
        return None
    
    def writeMDP(self) -> None:
        fl = list()
        for arg in self.mdpArguments:
            if type(self.mdpArguments[arg]) == list:
                c = ' '.join([*self.mdpArguments[arg]])
                fl += f'{arg} = {c}\n'
            else:
                fl += f'{arg} = {self.mdpArguments[arg]}\n'
        self.mdpFile.unlink()
        with open(self.mdpFile, 'w') as f:
            f.writelines(fl)

        return None
    
    def determineCenter(self) -> None:
        # first establish relationships between atom ID and molecule groups. 
        coll = dict()
        u = mda.Universe(self.updatedFile[0])
        with open(self.indexF) as f:
            for line in f.readlines():
                if '[' in line:
                    current = line.split()[1]
                    coll[current] = []
                else:
                    for n in line.split():
                        coll[current].append(int(n) - 1)

        # determine COM of liposome group
        lipdAG = AtomGroup([u.atoms[x] for x in coll['MM']])
        ref = lipdAG.center_of_mass()
        # find atom nearest the liposome com
        minimumV, mini = norm(ref - lipdAG[0].position) / 10, lipdAG[0]
        for a in lipdAG:
            if (norm(ref - a.position) / 10) < minimumV:
                mini = a
        # get molecule number of this atom
        self.additional['pull_group2_pbcatom'] = mini.resid
        # set that argument self.additional


    def setMDP(self) -> None:
        """
        Set Custom or Premade MDP
        """
        preconstructed = {'EM': Path('lib/baseScripts/EM.mdp'), 'NVT': Path('lib/baseScripts/NVT.mdp'), 'EQUIL': Path('lib/baseScripts/EQUIL.mdp'), 'NPT_015': Path('lib/baseScripts/NPT_015.mdp'), 'MD': Path('lib/baseScripts/MD.mdp'),
                          'EM_AA': Path('lib/baseScripts/EM_AA.mdp'), 'NVT_AA': Path('lib/baseScripts/NVT_AA.mdp'), 'NPT_AA': Path('lib/baseScripts/NPT_AA.mdp'), 'MD_AA': Path('lib/baseScripts/MD_AA.mdp'),
                          'PULL': Path('lib/baseScripts/PULL.mdp'), 'PULL_US': Path('lib/baseScripts/PULL_US.mdp'), 'PULL_EQUIL': Path('lib/baseScripts/PULL_EQUIL.mdp'), 'EM_US': Path('lib/baseScripts/EM_US.mdp'), 'EQUIL_5': Path('lib/baseScripts/EQUIL_5.mdp'), 'EQUIL_10': Path('lib/baseScripts/EQUIL_10.mdp'), 'EQUIL_15': Path('lib/baseScripts/EQUIL_15.mdp')} # add US specific cmnds
        if self.type in preconstructed:
            src = preconstructed[self.type].resolve()
            dest = Path(self.outLocation / Path(f'{self.type}.mdp'))
            shutil.copy(src,dest)
            self.mdpFile = dest
        elif 'mdp_ftype' in self.additional:
            src = Path(self.additional['mdp_fname']).resolve()
            dest = Path(self.outLocation / f'{src.stem}.mdp')
            shutil.copy(src,dest)
            self.mdpFile = dest
        else:   
            print('Please provide a valid MDP File')

    def process(self) -> None:
        if self.type == 'CONFIG':
            return None
        if self.US:
            self.determineCenter()
        self.parseMDP()
        if len(self.additional) != 0:
            self.updateMDP()
            self.writeMDP()
        if not self.US:
            self.genTPR(self.type)

    def generateFrames(self) -> None:
        # make new directory to house configurations
        # specific command / loop, invovles using last updated frame, only if type is FrameGen -> the updatedFiles from here actually then turn into a directory
        # first get the contents of disExtractor.py
        o = self.outLocation / 'dist.xvg'
        distance(self.trajectory, self.prevTPR, self.indexF, self.additional['lipid'], self.additional['drug'], o)
        data = []
        with open(o) as f:
            for line in f:
                if line.startswith(('#', '@')):
                    continue
                time, dist = map(float, line.strip().split())
                data.append((time, dist))

        data = np.array(data)
        times = data[:, 0]
        dists = data[:, 1]

        min_dist = np.min(dists)
        max_dist = np.max(dists)

        # --- Define dense regions and spacing ---
        dense_regions = [
            (2, 4, 0.05)     # Region 2: slightly coarser
        ]
        sparse_spacing = 0.05

        # --- Generate all target distances ---
        target_dists = []

        # Add dense region spacings
        for start, end, spacing in dense_regions:
            target_dists += list(np.arange(start, end + spacing, spacing))

        # Add sparse regions
        current = np.ceil(min_dist * 10) / 10
        dense_edges = sorted([(start, end) for start, end, _ in dense_regions])

        for start, end in dense_edges:
            while current < start:
                target_dists.append(current)
                current += sparse_spacing
            current = end + sparse_spacing  # skip over dense region

        while current <= np.floor(max_dist * 10) / 10:
            target_dists.append(current)
            current += sparse_spacing

        # Remove duplicates and sort
        target_dists = sorted(set(np.round(target_dists, 4)))  # round to avoid float precision overlap

        # --- Match target distances to closest frames ---
        selected = []
        used_indices = set()
        for target in target_dists:
            idx = (np.abs(dists - target)).argmin()
            if idx not in used_indices:
                selected.append((target, times[idx]))
                used_indices.add(idx)

        for dist, time in selected:
            if dist < 11:
                o = Path(self.outLocation / f'{dist}.gro').absolute()
                #extractFrame(self.trajectory, self.prevTPR, time, o, self.indexF)
                self.configNames.append(o)
        selected = [x for x in selected if x[0] < 11]
        # extract frame batching 
        p = self.chunk(selected, 5)
        for chunk in p:
            dist, time = " ".join([str(x[0]) for x in chunk]), " ".join([str(x[1]) for x in chunk])
            o = " ".join([str(Path(self.outLocation / f'{d}.gro').absolute()) for d in [x[0] for x in chunk]])
            job_script = f"""#!/bin/bash
            module purge
            source /smithlab/opt/gromacs/GMXRC2025
            outputs=({o})
            times=({time})
            for i in "${{!outputs[@]}}"; do
                o="${{outputs[$i]}}"
                t="${{times[$i]}}"
                echo "0" | gmx trjconv -s {self.prevTPR} -f {self.trajectory} -dump "$t" -o "$o" -n {self.indexF}
            done
            """
            subprocess.run(["sbatch", "--job-name=FRAMEGEN", "--output=output_%j.log", "--ntasks=1", "--cpus-per-task=4",
                    "--mem=12gb", "--partition=mw256", "--mail-user=hhabib@wesleyan.edu", "--mail-type=END,FAIL"], input=job_script.encode())

        f = False
        while f == False:
            f = self.statusCheck(self.configNames, self.outLocation)

    def umbrellaSpecific(self, frames, rType) -> None:
        frames = [str(x.absolute()) for x in frames]
        print(frames)
        frame_str = " ".join(frames)
        dists = " ".join([x.split('/')[-1][:-4] for x in frames])
        dists_l = [x.split('/')[-1][:-4] for x in frames]

        job_script = f"""#!/bin/bash
        module purge
        source /smithlab/opt/gromacs/GMXRC2025

        export GMX_GPU_DD_COMMS=true
        export GMX_GPU_PME_PP_COMMS=true
        export GMX_FORCE_UPDATE_DEFAULT_GPU=true

        frames=({frame_str})
        distances=({dists})
        rType="{rType}"

        for i in "${{!frames[@]}}"; do
            f="${{frames[$i]}}"
            d="${{distances[$i]}}"
            base=$(basename "$d")
            
            echo "Processing $f (distance: $d)..."
            srun gmx grompp -f {self.mdpFile} -c "$f" -r "$f" -p {self.system.topology} -n {self.indexF} -o "${{base}}.tpr" -maxwarn 10

            if [ "$rType" == "EM_US" ]; then
                echo "Running EM..."
                srun gmx mdrun -deffnm "${{base}}" -ntmpi 1 -ntomp 6 -nb gpu -pin off -v
            else
                echo "Running non-EM..."
                srun gmx mdrun -deffnm "${{base}}" -ntmpi 1 -ntomp 6 -nb gpu -pin off -v -bonded gpu
            fi
        done
        """
        for d in dists_l:
            o = self.outLocation / f"{d}.gro"
            self.configNames.append(o)
        print(self.configNames)
        subprocess.run(["sbatch", "--job-name=SUBJOB", "--output=output_%j.log", "--ntasks=1", "--cpus-per-task=6", "--gpus-per-node=1",
                        "--mem=32gb", "--gres=gpu:1", "--partition=mwgpu256,exx96", "--mail-user=hhabib@wesleyan.edu", "--mail-type=END,FAIL"], input=job_script.encode())
        return None
    def chunk(self, lst, n) -> None:
        k, m = divmod(len(lst), n)
        return [lst[i*k + min(i, m):(i+1)*k + min(i+1, m)] for i in range(n)]


    def errorStartUp(self, name) -> bool:
        # incase of failure, restart from CPT file! # only for md run, a failure in anyother run, NPT, EM, NVT is iindicative of a deeper problem
        if not Path(self.outLocation / f"{name}.gro").exists():
            runMDCPT(name, 1, 'off', 12, f'{name}.cpt') # instead of startup, just return false and keep waiting
            return False
        return True

    
    def genTPR(self, name) -> None:
        o = Path(self.outLocation / f"{name}.tpr").absolute()
        makeTPR(self.mdpFile, self.system.SystemManager.latestFile[0], self.system.topology, o, self.indexF)
        return None
        
    def statusCheck(self, src:list, dest:Path) -> None:
        dest = Path(dest)
        return all((dest / Path(f).name).exists() for f in src)

    def gmxCommand(self, name) -> None:
        os.chdir(self.outLocation)
        #runMD_CPU(self.type, 10)
        if self.US and self.type == 'CONFIG':
            self.generateFrames()
            self.system.SystemManager.latestFile = [self.configNames]
            return None
        if self.US:
            p = self.chunk(self.system.SystemManager.latestFile, 15)
            for c in p:
                self.umbrellaSpecific(c, self.type)
            f = False
            while f == False:
                f = self.statusCheck(self.configNames, self.outLocation)
            self.system.SystemManager.latestFile = [self.configNames]
            return None
        else:
            runMD(name, 1, 'off', 12)
            f = False
            while f == False:
                f = self.errorStartUp(name)
            return None

    def run(self):
        self.process()
        self.gmxCommand(self.type)

    def retrieveLatestFile(self):
        if self.US:
            return [self.system.SystemManager.latestFile] # whole directory
        else:
            o = Path(self.outLocation / f"{self.type}.gro")
            t = Path(self.outLocation / f"{self.type}.xtc")
            tpr = Path(self.outLocation / f"{self.type}.tpr")
            return [o, t, tpr]

