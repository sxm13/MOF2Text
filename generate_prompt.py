import os

os.environ.setdefault("MKL_NUM_THREADS", "8")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "8")
os.environ.setdefault("OMP_NUM_THREADS", "8")
os.environ.setdefault("MKL_THREADING_LAYER", "GNU")

import argparse
import glob
import json
import shutil
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

from mof2text.run import FEATURES, normalize_features, get_prompt_parts, join_parts

FEATURE_HELP = {
    "base": "chemical formula, cell parameters, space group",
    "topology": "dimensionality, interpenetration, topology (CrystalNets/Julia)",
    "bbs": "inorganic/organic building blocks and solvents (MOFid + Robocrys)",
    "pore": "LCD, PLD, surface area, void fraction, pore volume (Zeo++)",
    "charge": "partial atomic charge ranges (PACMAN)",
}


def collect_cifs(inputs):
    cifs = []
    for item in inputs:
        if os.path.isdir(item):
            cifs += sorted(glob.glob(os.path.join(item, "*.cif")))
        elif any(c in item for c in "*?["):
            cifs += sorted(glob.glob(item))
        elif os.path.isfile(item):
            cifs.append(item)
        else:
            print(f"[warning] not found: {item}", file=sys.stderr)
    seen, out = set(), []
    for c in cifs:
        if c.endswith("_pacman.cif"):
            continue
        key = os.path.abspath(c)
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def n_atoms(cif):
    from ase.io import read
    return len(read(cif))


def build_parser():
    p = argparse.ArgumentParser(
        description="Generate MOF2Text descriptions from CIF files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="features:\n" + "\n".join(f"  {k:<9} {v}" for k, v in FEATURE_HELP.items()),
    )
    p.add_argument("inputs", nargs="*", help="CIF files, folders, or glob patterns")
    p.add_argument("-f", "--features", nargs="+", default=["all"],
                   help="features to include, space- or comma-separated (default: all)")
    p.add_argument("-o", "--output-dir", help="write one <cif_id>.json per CIF into this folder")
    p.add_argument("--jsonl", help="append all results to this JSONL file")
    p.add_argument("--save-parts", action="store_true",
                   help="also store the text of each feature separately in the JSON")
    p.add_argument("--skip-existing", action="store_true",
                   help="skip CIFs whose JSON already exists in --output-dir")
    p.add_argument("--max-atoms", type=int, default=None,
                   help="skip structures with more atoms than this (e.g. 500)")
    p.add_argument("--keep-intermediate", action="store_true",
                   help="keep the <cif_id>/ folders created by bbs/charge")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="show the console output of MOFid / CrystalNets / PACMAN / Zeo++")
    p.add_argument("--log", default=None,
                   help="save that (normally hidden) output to this log file")
    p.add_argument("--list-features", action="store_true", help="list features and exit")

    g = p.add_argument_group("pore options (Zeo++)")
    g.add_argument("--probe-radius", type=float, default=0.0, help="probe radius in Å (default 0)")
    g.add_argument("--chan-radius", type=float, default=0.0, help="channel radius in Å (default 0)")
    g.add_argument("--num-samples", type=int, default=5000, help="Monte Carlo samples (default 5000)")

    g = p.add_argument_group("charge options (PACMAN)")
    g.add_argument("--charge-type", default="DDEC6", help="DDEC6, Bader, CM5 or REPEAT (default DDEC6)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)

    if args.list_features:
        for k, v in FEATURE_HELP.items():
            print(f"{k:<9} {v}")
        return 0
    if not args.inputs:
        build_parser().error("no input CIF given")

    try:
        features = normalize_features(args.features)
    except ValueError as e:
        build_parser().error(str(e))

    feature_kwargs = {
        "pore": {"probe_radius": args.probe_radius,
                 "chan_radius": args.chan_radius,
                 "num_samples": args.num_samples},
        "charge": {"charge_type": args.charge_type},
    }

    cifs = collect_cifs(args.inputs)
    if not cifs:
        print("No CIF files found.", file=sys.stderr)
        return 1

    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
    jsonl = open(args.jsonl, "a", encoding="utf-8") if args.jsonl else None
    to_stdout = not args.output_dir and not args.jsonl

    try:
        from tqdm import tqdm
        iterator = tqdm(cifs, desc="MOF2Text", disable=to_stdout or len(cifs) == 1)
    except ImportError:
        iterator = cifs

    print(f"features: {', '.join(features)} | {len(cifs)} CIF(s)", file=sys.stderr)
    n_ok = n_skip = n_fail = 0

    for cif in iterator:
        cif_id = Path(cif).stem
        out_json = os.path.join(args.output_dir, cif_id + ".json") if args.output_dir else None

        if args.skip_existing and out_json and os.path.exists(out_json):
            n_skip += 1
            continue

        if args.max_atoms is not None:
            try:
                n = n_atoms(cif)
            except Exception as e:
                print(f"[fail] {cif_id}: cannot read CIF ({e})", file=sys.stderr)
                n_fail += 1
                continue
            if n > args.max_atoms:
                print(f"[skip] {cif_id}: {n} atoms > {args.max_atoms}", file=sys.stderr)
                n_skip += 1
                continue

        work_dir = Path(cif_id)
        existed = work_dir.exists()
        try:
            parts = get_prompt_parts(cif, features, feature_kwargs,
                                     quiet=not args.verbose, log_file=args.log)
            text = join_parts(parts)
            record = {"cif_id": cif_id, "features": features, "mof2text": text}
            if args.save_parts:
                record["parts"] = parts

            if to_stdout:
                print(f"{cif_id}: {text}\n")
            if out_json:
                with open(out_json, "w", encoding="utf-8") as f:
                    json.dump(record, f, ensure_ascii=False, indent=2)
            if jsonl:
                jsonl.write(json.dumps(record, ensure_ascii=False) + "\n")
                jsonl.flush()

            empty = [k for k, v in parts.items() if not v or v == "."]
            if empty:
                print(f"[warning] {cif_id}: no text for {', '.join(empty)}", file=sys.stderr)
            n_ok += 1
        except Exception as e:
            print(f"[fail] {cif_id}: {e}", file=sys.stderr)
            n_fail += 1
        finally:
            if not args.keep_intermediate and not existed and work_dir.is_dir():
                shutil.rmtree(work_dir, ignore_errors=True)

    if jsonl:
        jsonl.close()
    print(f"done: {n_ok} ok, {n_skip} skipped, {n_fail} failed", file=sys.stderr)
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
