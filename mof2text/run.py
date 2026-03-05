import warnings

warnings.filterwarnings('ignore')

from mof2text.base_info.merge import prompt_1st
from mof2text.topology.merge import prompt_2nd
from mof2text.bbs.merge import prompt_3rd
from mof2text.charges.merge import prompt_4th


def _as_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    attr = "prompt"
    if hasattr(x, attr):
        v = getattr(x, attr)
        if v is None:
            return ""
        if isinstance(v, str):
            return v
        return str(v)

    return str(x)


def get_prompt(cif_path: str) -> str:
    p1 = prompt_1st(cif_path)
    p2 = prompt_2nd(cif_path)
    p3 = prompt_3rd(cif_path)
    p4 = prompt_4th(cif_path)
    
    parts = []
    
    text1 = _as_text(p1).strip()


    text2 = _as_text(p2).strip()
    text3 = _as_text(p3).strip()
    
    text4 = _as_text(p4).strip()
    
    parts = [text1, text2 + text3, text4]
    
    return " ".join(parts)