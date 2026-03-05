import os
import juliacall


os.environ["JULIA_DEPOT_PATH"] = os.getcwd()

juliacall.Main.seval('import Pkg; Pkg.add("CrystalNets")')

jl = juliacall.newmodule("topo")
jl.seval("using CrystalNets")


def get_topo(structure):

    clustering = jl.Clustering.AllNodes
    options = jl.CrystalNets.Options(structure=jl.StructureType.MOF,
                                     clusterings=[clustering])
    result = jl.determine_topology(structure, options)

    result_tp = {"dimension": [],
                 "topology": [],
                 "catenation": []}
    interpenetration = jl.CrystalNets.total_interpenetration(result,
                                                             clustering)

    for x in result:
        info = x[0][clustering]
        result_tp["dimension"].append(jl.ndims(info.genome))
        result_tp["catenation"].append(interpenetration[info])
        s = str(info)
        result_tp["topology"].append(s if len(s) < 6 else "unnamed")

    return result_tp
