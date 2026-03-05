import os
from ase.io import read
from mofid.id_constructor import extract_fragments
import networkx as nx
from ase import neighborlist
from ase.build import sort


def dict2str(dct):

    return ''.join(symb + (str(n)) for symb, n in dct.items())


def get_node_linker_files(cif_path, prefix):

    os.makedirs(prefix, exist_ok=True)
    extract_fragments(cif_path, prefix)
    nodes = read(os.path.join(prefix, "AllNode/nodes.cif"))
    linkers = read(os.path.join(prefix, "AllNode/linkers.cif"))
    try:
        free_solvs = read(os.path.join(prefix, "AllNode/free_solvent.cif"))
    except:
        free_solvs = None
    try:
        bound_solvs = read(os.path.join(prefix, "AllNode/bound_solvent.cif"))
    except:
        bound_solvs = None
    return nodes, linkers, free_solvs, bound_solvs


def get_solvent_or_ion(atoms):
    if atoms is None:
        return 0
    try:
        return len(atoms)
    except TypeError:
        return 0


def split_bbs(atoms):

    cutOff = neighborlist.natural_cutoffs(atoms)
    neighborList = neighborlist.NeighborList(cutOff, self_interaction=False, bothways=True, skin=0.3)
    neighborList.update(atoms)
    G = nx.Graph()
    for k in range(len(atoms)):
        tup = (k, {"element": "{}".format(atoms.get_chemical_symbols()[k]), 
                   "pos": atoms.get_positions()[k]})
        G.add_nodes_from([tup])
    for k in range(len(atoms)):
        for i in neighborList.get_neighbors(k)[0]:
            G.add_edge(k, i)
    Gcc = sorted(nx.connected_components(G), key=len, reverse=True)
    form_dicts = []
    fragments = []
    for g in Gcc:
        g = list(g)
        fragment = atoms[g]
        fragment = sort(fragment)
        fragments.append(fragment)
        form_dict = fragment.symbols.formula.count()
        form_dicts.append(dict2str(form_dict))
    bbs = []
    unique_formdicts = []
    n_bbs = []
    for index, form_dict in enumerate(form_dicts):
        if form_dict not in unique_formdicts:
            bbs.append(fragments[index])
            unique_formdicts.append(form_dict)
            n_bbs.append(1)
        else:
            idx = unique_formdicts.index(form_dict)
            n_bbs[idx] += 1
    return bbs, n_bbs
