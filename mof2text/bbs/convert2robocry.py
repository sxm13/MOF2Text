from robocrys import StructureCondenser, StructureDescriber
from pymatgen.io.ase import AseAtomsAdaptor


def get_desc(atoms):
    
    struc = AseAtomsAdaptor.get_structure(atoms)
    condenser = StructureCondenser()
    describer = StructureDescriber()
    condensed_structure = condenser.condense_structure(struc)
    description = describer.describe(condensed_structure)
    return description