import importlib
import warnings

from mof2text.utils import suppress_output

warnings.filterwarnings('ignore')


# feature name -> (module, attribute). Imported lazily so that unselected
# features (e.g. Julia for topology, PACMAN for charges) are never loaded.
_REGISTRY = {
    "base": ("mof2text.base_info.merge", "prompt_1st"),
    "topology": ("mof2text.topology.merge", "prompt_2nd"),
    "bbs": ("mof2text.bbs.merge", "prompt_3rd"),
    "pore": ("mof2text.pore.merge", "prompt_5th"),
    "charge": ("mof2text.charges.merge", "prompt_4th"),
}

# canonical order of the sentences in the final text
FEATURES = ("base", "topology", "bbs", "pore", "charge")

_ALIASES = {
    "base_info": "base", "basic": "base", "cell": "base",
    "topo": "topology",
    "bb": "bbs", "building_blocks": "bbs", "building_block": "bbs",
    "pores": "pore", "porosity": "pore",
    "charges": "charge", "pacman": "charge",
}


def normalize_features(features=None):
    """Accept None/'all', a comma string, or an iterable; return canonical,
    de-duplicated features in FEATURES order."""
    if features is None:
        return list(FEATURES)
    if isinstance(features, str):
        features = [features]
    names = []
    for item in features:
        for f in str(item).split(","):
            f = f.strip().lower()
            if not f:
                continue
            if f == "all":
                return list(FEATURES)
            f = _ALIASES.get(f, f)
            if f not in _REGISTRY:
                raise ValueError(f"Unknown feature '{f}'. "
                                 f"Choose from: {', '.join(FEATURES)} (or 'all').")
            names.append(f)
    if not names:
        raise ValueError("No feature selected.")
    return [f for f in FEATURES if f in names]


def _load(feature):
    module, attr = _REGISTRY[feature]
    return getattr(importlib.import_module(module), attr)


def _as_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    if hasattr(x, "prompt"):
        v = getattr(x, "prompt")
        if v is None:
            return ""
        return v if isinstance(v, str) else str(v)
    return str(x)


def get_prompt_parts(cif_path, features=None, feature_kwargs=None,
                     quiet=True, log_file=None):
    """Return {feature: text} for the selected features (empty string on failure).

    quiet:    hide the console output of MOFid / CrystalNets / PACMAN / Zeo++.
    log_file: append that hidden output to this file instead of discarding it.

    feature_kwargs: optional {feature: {kwarg: value}} passed to that feature,
    e.g. {"pore": {"probe_radius": 1.86, "chan_radius": 1.86},
          "charge": {"charge_type": "DDEC6"}}
    """
    feature_kwargs = feature_kwargs or {}
    parts = {}
    for f in normalize_features(features):
        kwargs = feature_kwargs.get(f, {})
        try:
            with suppress_output(log_file, enabled=quiet):
                parts[f] = _as_text(_load(f)(cif_path, **kwargs)).strip()
        except Exception:
            parts[f] = ""
    return parts


def join_parts(parts):
    """Assemble per-feature texts into one paragraph."""
    topo = parts.get("topology", "")
    bbs = parts.get("bbs", "")
    if bbs in (".", ""):
        bbs = ""                       # bbs failed or not selected

    # topology and bbs form one sentence: "This ... topology, it contains ..."
    if topo and bbs:
        middle = topo + bbs
    elif topo:
        middle = topo + "."
    elif bbs:
        middle = "This framework contains " + bbs.split("it contains ", 1)[-1] \
            if bbs.startswith(", it contains") else bbs
    else:
        middle = ""

    ordered = [parts.get("base", ""), middle, parts.get("pore", ""), parts.get("charge", "")]
    return " ".join(p for p in ordered if p)


def get_prompt(cif_path: str, features=None, feature_kwargs=None,
               quiet=True, log_file=None) -> str:
    """Generate MOF2Text for a CIF. features=None means all features."""
    return join_parts(get_prompt_parts(cif_path, features, feature_kwargs,
                                       quiet=quiet, log_file=log_file))
