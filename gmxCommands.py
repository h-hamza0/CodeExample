# Library of most used gmx commands. SH -> Py
import subprocess
from pathlib import Path
import os
def cg2atConvert(cgFile, destinationPath):
    original=os.getcwd() # original path
    commands='12\n10\n2\n' # hard coded, difficult to directly interface with
    destination=destinationPath.absolute() # desitination path
    # change dir to destination path
    os.makedirs(destination, exist_ok=True)
    os.chdir(destination)
    subprocess.run(['srun', 'cg2at', '-c', f'{cgFile.absolute()}', '-gmx', 'gmx', '-loc', 'CG'], input=commands,text=True)
    # get the path of the cg2at final
    convertedStruct = Path(destinationPath) / "CG" / "FINAL" / "final_cg2at_de_novo.pdb"
    os.chdir(original)
    # send it back up
    return convertedStruct.absolute()
    # change os path back to original

def ionize(initialFile, outputTPR, output,  ionsMDP, topology):
    # generate tpr file
    subprocess.run(['srun', 'gmx', 'grompp', '-f', f'{ionsMDP}', '-c', f'{initialFile}', '-p', f'{topology}', '-o', f'{outputTPR}'])
    subprocess.run(['srun', 'gmx', 'genion', '-s', f'{outputTPR}', '-o', f'{output}', '-p', f'{topology}', '-pname', 'SOD', '-nname', 'CLA', '-neutral'], input='5\n', text=True)
    # genion

def insert_molecules(insertMolecule, output, boxSize, number, radius, inputFile=None, writeFile=None):
    if inputFile != None:
        subprocess.run(['srun', 'gmx', 'insert-molecules', '-f', f'{inputFile}', '-ci', f'{insertMolecule}',
                        '-o', f'{output}', '-nmol', f'{number}', '-radius', f'{radius}', '-try', '500'])
        if writeFile != None:
            with open(writeFile, 'w') as f:
                f.write(f'gmx insert-molecules -f {inputFile} -ci {insertMolecule} -o {output} -nmol {number} -radius {radius} -try 500')
    else:
        subprocess.run(['srun', 'gmx', 'insert-molecules', '-ci', f'{insertMolecule}',
                        '-o', f'{output}', '-box', f'{boxSize[0]}', f'{boxSize[1]}', f'{boxSize[2]}', '-nmol', f'{number}',
                        '-radius', f'{radius}', '-try', '500'])
        if writeFile != None:
            with open(writeFile, 'w') as f:
                f.write(f'gmx insert-molecules -ci {insertMolecule} -o {output} -box {boxSize[0]} {boxSize[1]} {boxSize[2]} -nmol {number} -radius {radius}')
    return None

def center_setup(inputFile, outputFile, edgeDistance) -> None:
    subprocess.run(['srun', 'gmx', 'editconf', '-f', f'{inputFile}', '-o', f'{outputFile}', '-c', '-box', f'{edgeDistance[0]}',f'{edgeDistance[1]}', f'{edgeDistance[2]}', '-pbc', 'yes', '-bt', 'cubic'])
    return None

def solvAA(inputFile, waterModel, topology, output) -> None:
    subprocess.run(['srun', 'gmx','solvate', '-cp', f'{inputFile}','-cs', f'{waterModel}.gro', '-p', f'{topology}', '-o', f'{output}'])
    return None

def minimal_setup(inputFile, outputFile, edgeDistance) -> None:
    subprocess.run(['srun', 'gmx', 'editconf', '-f', f'{inputFile}', '-o', f'{outputFile}', '-c', '-d',f'{edgeDistance}','-pbc', 'yes', '-bt', 'cubic'])
    return None

def packMol(inputFile_a, inputFile_b, outputFile, distance, parent) -> None:
    inp = f"""
    tolerance 2.0
    output {outputFile}
    filetype pdb
    structure {inputFile_a}
        number 1
        fixed 0. 0. 0. 0. 0. 0.
    end structure

    structure {inputFile_b}
        number 1
        fixed {distance}. 0. 0. 0. 0. 0.
    end structure
    """
    # have to write file .....
    inpF = Path(parent / 'setup' / 'pack.inp').absolute()
    with open(inpF, 'w') as f:
        f.writelines(inp)

    subprocess.run(['srun', 'packmol', '-i', f'{inpF}'])

def solvate(inputFile, waterFile, writtenTopology, outputFile, radius) -> None:
    subprocess.run(['srun', 'gmx', 'solvate','-cp', f'{inputFile}', '-cs', f'{waterFile}', '-p', f'{writtenTopology}', '-o', f'{outputFile}', '-radius', f'{radius}'])
    return None

def distance(inputFile, tprFile, indexFile, lipid, drug, output) -> None:
    subprocess.run(['srun', 'gmx', 'distance', '-s', f'{tprFile}', '-f', f'{inputFile}', '-n', f'{indexFile}', '-select', f'com of group "{lipid}" plus com of group "{drug}"', '-oall', f'{output}'])
    return None

def convertPDB(inputFile, outputFile) -> None:
    subprocess.run(['srun', 'gmx', 'editconf', '-f', f'{inputFile}', '-o', f'{outputFile}'])
    return None

def extractFrame(inputFile, tprFile, time, name, indexFile) -> None:
    subprocess.run(['srun', 'gmx', 'trjconv', '-s', f'{tprFile}', '-f', f'{inputFile}', '-dump', f'{time}', '-o', f'{name}', '-n', f'{indexFile}'], input='0\n', text=True)
    return None

def makeTPR(inputFile, initialGeometry, topology, outputFile, index=None) -> None:
    if index == None:
        subprocess.run(['srun', 'gmx', 'grompp', '-f', f'{inputFile}', '-c', f'{initialGeometry}', '-p', f'{topology}', '-o', f'{outputFile}' , '-maxwarn', '10', '-r', f'{initialGeometry}'])
    else:
        subprocess.run(['srun', 'gmx', 'grompp', '-f', f'{inputFile}', '-c', f'{initialGeometry}', '-p', f'{topology}', '-o', f'{outputFile}', '-n', f'{index}', '-maxwarn', '10', '-r', f'{initialGeometry}'])
    return None

def runMD_CPU(defaultName, threads_omp):
    subprocess.run(['srun', 'gmx', 'mdrun', '-deffnm', f'{defaultName}', '-ntomp', '4', '-v', '-ntmpi', '1', '-nb', 'gpu', '-pin', 'on', '-cpt', '5', '-pme', 'gpu'])
    return None

def runMD(defaultName, threads_mpi, pin, threads_omp):
    subprocess.run(['srun', 'gmx', 'mdrun', '-deffnm', f'{defaultName}', '-ntmpi', f'{threads_mpi}', '-pin', f'{pin}', '-ntomp', f'{threads_omp}', '-v', '-nb', 'gpu'])
    return None

def runMDCPT(defaultName, threads_mpi, pin, threads_omp, cpt):
    subprocess.run(['srun', 'gmx', 'mdrun', '-deffnm', f'{defaultName}', '-ntmpi', f'{threads_mpi}', '-pin', '{pin}', '-ntomp', f'{threads_omp}', '-cpi', f'{cpt}',  '-nb', 'gpu', '-cpt', '5', '-v'])
    return None

def makeIndex(reference, output, associations):
    # first make blank index file
    subprocess.run(['srun', 'gmx', 'make_ndx', '-f', f'{reference}', '-o', f'{output}'],
                   input = 'q\n', text=True)
    # parse index file to retrieve names of groups
    existing = dict() # {group: id} # from here we can determine which group are which id numbers
    with open(output, 'r') as f:
        lns = f.readlines()
    c = 0
    for l in lns:
        if l[0] == '[':
            existing[l.split()[1]] = c
            c += 1

    # pre check if names in index file:
    for g in associations:
        for grps in g:
            print(grps)
            print(g[grps])
            for subG in g[grps]:
                if subG not in existing:
                    print(f'Group {subG} not in system! Check group defintions')
                    return KeyError
    # build option:

    command = ""
    for g in associations:
        for grps in g:
            option = ""
            for subG in g[grps]:
                option += f"{existing[subG]}|"
            option = option[:-1] + '\n'
            option += f"name {c} {grps}\n"
            command += option
            c += 1
    #command += f'9 & a NC3 | a NH3 | a PO4\nname {c} CORE\n'
    command += 'q\n'

    subprocess.run(['srun', 'gmx', 'make_ndx', '-f', f'{reference}', '-o', f'{output}'],
                   input = command, text=True)
    
    return None
