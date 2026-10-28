import os
import re
import shutil
import subprocess
import tempfile


def _run_network(structure, flag_args, suffix):

    structure = os.path.abspath(structure)
    tmp_dir = tempfile.mkdtemp(prefix="mof2text_zeopp_")
    out_file = os.path.join(tmp_dir, f"out.{suffix}")
    try:
        cmd = ["network", "-ha", *map(str, flag_args), out_file, structure]
        subprocess.run(cmd,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       check=True,
                       cwd=tmp_dir,
                       )
        with open(out_file) as f:
            return f.read()
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def _grab(text, key):
    m = re.search(re.escape(key) + r"\s*([-+0-9.eE]+)", text)
    if m is None:
        raise ValueError(f"'{key}' not found in Zeo++ output")
    return float(m.group(1))


def PoreDiameter(structure):

    out = _run_network(structure, ["-res"], "res")
    vals = out.split()
    lcd, pld, lfpd = map(float, vals[1:4])
    return {"LCD": lcd, "PLD": pld, "LFPD": lfpd}


def SurfaceArea(structure, chan_radius=0.0, probe_radius=0.0, num_samples=5000):

    out = _run_network(structure,
                       ["-sa", chan_radius, probe_radius, num_samples],
                       "sa")
    first = out.splitlines()[0]
    return {"density": _grab(first, "Density:"),
            "ASA_A2": _grab(first, "ASA_A^2:"),
            "ASA_m2_cm3": _grab(first, "ASA_m^2/cm^3:"),
            "ASA_m2_g": _grab(first, "ASA_m^2/g:"),
            }


def PoreVolume(structure, chan_radius=0.0, probe_radius=0.0, num_samples=5000):

    out = _run_network(structure,
                       ["-volpo", chan_radius, probe_radius, num_samples],
                       "volpo")
    first = out.splitlines()[0]
    return {"density": _grab(first, "Density:"),
            "POAV_A3": _grab(first, "POAV_A^3:"),
            "POAV_fraction": _grab(first, "POAV_Volume_fraction:"),
            "POAV_cm3_g": _grab(first, "POAV_cm^3/g:"),
            }
