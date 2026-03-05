from mof2text.charges.runner import get_labels_charges
from collections import defaultdict
from pathlib import Path


class prompt_4th():

    def __init__(self,
                 cif_path,
                 charge_type="DDEC6",
                 digits=10,
                 atom_type=True, 
                 neutral=True,
                 keep_connect=False):
        
        self.cif_path = cif_path
        self.charge_type = charge_type
        self.digits = digits
        self.atom_type = atom_type
        self.neutral = neutral
        self.keep_connect = keep_connect
        self.prefix = Path(self.cif_path).stem

        self.labels, self.charges = self.get_info()
        
        if self.charges is not None:
            self.prompt = self.process()
        else:
            self.prompt = None

    def get_info(self):
        try:
            labels, charges = get_labels_charges(self.cif_path,
                            self.charge_type,
                            self.digits,
                            self.atom_type,
                            self.neutral,
                            self.keep_connect,
                            self.prefix
                            )
        except:
            labels, charges = None, None

        return labels, charges
    

    @staticmethod
    def _fmt_range(xmin, xmax, ndp=2):
        if round(float(xmin), ndp) == round(float(xmax), ndp):
            return f"{float(xmin):.{ndp}f}"
        return f"{float(xmin):.{ndp}f} to {float(xmax):.{ndp}f}"
    
    
    def summary_data(self):
        stats = defaultdict(lambda: {"min": None, "max": None})
        for k, v in zip(self.labels, self.charges):
            s = stats[k]
            s["min"] = v if s["min"] is None else min(s["min"], v)
            s["max"] = v if s["max"] is None else max(s["max"], v)
        return stats


    def process(self, ndp=2, sort_elements=True):
        stats = self.summary_data()
        elements = list(stats.keys())
        if sort_elements:
            elements = sorted(elements)
        elems_text = ", ".join(elements)
        ranges_text = ", ".join(
            self._fmt_range(stats[e]["min"], stats[e]["max"], ndp=ndp)
            for e in elements
        )
        text_ = (
            f"The partial atomic charge ranges for {elems_text} are "
            f"{ranges_text}."
        )
        return text_


    def __str__(self):
        return self.prompt or ""


    def __repr__(self):
        return f"prompt_4th(text={self.prompt!r})"