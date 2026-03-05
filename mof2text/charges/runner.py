from PACMANCharge import pmcharge
from gemmi import cif
import os, shutil

def get_labels_charges(cif_path,
                      charge_type,
                      digits,
                      atom_type, 
                      neutral,
                      keep_connect,
                      prefix):

    pmcharge.predict(cif_path,
                    charge_type,
                    digits,
                    atom_type, 
                    neutral,
                    keep_connect)

    cif_pacman_path = cif_path.replace(".cif", "_pacman.cif")
    new_cif_path = os.path.join(prefix,
                                os.path.basename(cif_pacman_path)
                                )
    os.makedirs(prefix, exist_ok=True)
    if os.path.exists(new_cif_path):
        os.remove(new_cif_path)
    shutil.move(cif_pacman_path, prefix)
    doc = cif.read_file(filename=str(new_cif_path))
    block = doc.sole_block()
    labels = block.find_loop("_atom_site_type_symbol")
    charges = block.find_loop("_atom_site_charge")

    atoms = []
    atomic_charges = []
    for label in labels:
        atoms.append(label)
    for charge in charges:
        atomic_charges.append(float(charge))

    return atoms, atomic_charges