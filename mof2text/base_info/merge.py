from mof2text.base_info.runner import *
from ase.io import read


def prompt_1st(cif_path):
    
    try:
        atoms = read(cif_path)
        cf = get_chem_formula(atoms)
        sg = get_space_group(atoms)
        abc, angles = get_cell_para(atoms)
        return (f'{cf} has unit-cell lengths of '
               f'{round(float(abc[0]), 4)} Å, {round(float(abc[1]), 4)} Å, and {round(float(abc[2]), 4)} Å '
               f'with cell angles of {round(float(angles[0]), 1)}°, {round(float(angles[1]), 1)}°, and {round(float(angles[2]), 1)}°, '
               f'and crystallizes in the {sg} space group.')
    except:
        return None