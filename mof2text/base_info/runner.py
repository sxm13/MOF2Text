from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer


def get_chem_formula(atoms):

    return atoms.get_chemical_formula(mode="hill")


def get_space_group(atoms):

    struct = AseAtomsAdaptor.get_structure(atoms)
    sga = SpacegroupAnalyzer(struct,
                             symprec=1e-3,
                             angle_tolerance=5
                             )
    sg_symbol = sga.get_space_group_symbol()
    return sg_symbol


def get_cell_para(atoms):

    return atoms.cell.lengths(), atoms.cell.angles()