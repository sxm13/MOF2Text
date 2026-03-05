from mof2text.bbs.split import *
from mof2text.bbs.convert2robocry import get_desc
from mof2text.base_info.runner import get_chem_formula
import re
from pathlib import Path


class prompt_3rd():

    def __init__(self, cif_path):
        self.cif_path = cif_path
        self.prefix = Path(cif_path).stem

        (self.unique_nodes,
         self.node_counts,
         self.unique_linkers,
         self.linker_counts,
         self.unique_free_solvs,
         self.free_solvs_counts,
         self.unique_bound_solvs,
         self.bound_solvs_counts) = self.mof_decompose()

        self.prompt_bbs = self.process_nodes_linkers() if self.unique_nodes is not None else "."
        
        self.prompt = self.prompt_bbs

    
    def mof_decompose(self):
        try:
            nodes, linkers, free_solvs, bound_solvs = get_node_linker_files(self.cif_path, self.prefix)
            unique_nodes, node_counts = split_bbs(nodes)
            unique_linkers, linker_counts = split_bbs(linkers)
            if get_solvent_or_ion(free_solvs) > 0:
                unique_free_solvs, free_solvs_counts = split_bbs(free_solvs)
            else:
                unique_free_solvs, free_solvs_counts = None, None
            if get_solvent_or_ion(bound_solvs) > 0:
                unique_bound_solvs, bound_solvs_counts = split_bbs(bound_solvs)
            else:
                unique_bound_solvs, bound_solvs_counts = None, None

            return (unique_nodes,
                    node_counts,
                    unique_linkers,
                    linker_counts,
                    unique_free_solvs,
                    free_solvs_counts,
                    unique_bound_solvs,
                    bound_solvs_counts
                    )
        except:
            return (None,) * 8
        

    def n_types(self, n: int, kind_: str) -> str:
        if n == 1:
            return f"one type of {kind_}"
        else:
            return f"{n} types of {kind_}s"
    

    def _get_molecule_parts(self):
        def _items(unique, counts):
            if unique is None or counts is None:
                return []
            
            if isinstance(counts, dict):
                return [(k, int(v)) for k, v in counts.items() if int(v) > 0]
            
            if isinstance(counts, (list, tuple)):
                if isinstance(unique, (list, tuple)):
                    return [(u, int(c)) for u, c in zip(unique, counts) if int(c) > 0]
                n = int(sum(counts))
                return [(unique, n)] if n > 0 else []
            
            n = int(counts)
            return [(unique, n)] if n > 0 else []
        
        parts = []
        
        for obj, n in _items(self.unique_free_solvs, self.free_solvs_counts):
            formula = get_chem_formula(obj) if obj else str(obj)
            parts.append(f"{n} free {'molecule' if n == 1 else 'molecules'} ({formula})")
        
        for obj, n in _items(self.unique_bound_solvs, self.bound_solvs_counts):
            formula = get_chem_formula(obj) if obj else str(obj)
            parts.append(f"{n} coordinated {'molecule' if n == 1 else 'molecules'} ({formula})")
        
        return parts


    def process_nodes_linkers(self):

        molecule_parts = self._get_molecule_parts()
        
        components = []
        components.append(self.n_types(len(self.node_counts), 'inorganic building block'))
        components.append(self.n_types(len(self.linker_counts), 'organic building block'))
        
        if molecule_parts:
            if len(molecule_parts) == 1:
                molecule_text = molecule_parts[0]
            elif len(molecule_parts) == 2:
                molecule_text = f"{molecule_parts[0]} and {molecule_parts[1]}"
            else:
                molecule_text = ", ".join(molecule_parts[:-1]) + f", and {molecule_parts[-1]}"

            text_summary = f", it contains {', '.join(components)}, {molecule_text}"
        else:
            text_summary = f", it contains {' and '.join(components)}"

        i = 1
        text_ = ""
        for node, n_node in zip(self.unique_nodes,
                                self.node_counts):
            cf = get_chem_formula(node)
            robocry_node = get_desc(node)
            m = re.match(r'\s*(?:[^.]*\.){2}\s*', robocry_node, flags=re.S)
            use_robocry = robocry_node[m.end():] if m else ""
            text_ += f" For {n_node} building blocks {i} ({cf}): "
            text_ += use_robocry
            i += 1

        for linker, n_linker in zip(self.unique_linkers,
                                self.linker_counts):
            cf = get_chem_formula(linker)
            robocry_linker = get_desc(linker)
            m = re.match(r'\s*(?:[^.]*\.){2}\s*',
                         robocry_linker,
                         flags=re.S)
            use_robocry = robocry_linker[m.end():] if m else ""
            text_ += f" For {n_linker} building blocks {i} ({cf}): "
            text_ += use_robocry
            i += 1

        return text_summary + "." + text_


    def __str__(self):
        return self.prompt or ""


    def __repr__(self):
        return f"prompt_3rd(text={self.prompt!r})"