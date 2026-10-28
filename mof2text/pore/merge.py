from mof2text.pore.runner import PoreDiameter, SurfaceArea, PoreVolume


class prompt_5th():

    def __init__(self,
                 cif_path,
                 chan_radius=0.0,
                 probe_radius=0.0,
                 num_samples=5000,
                 ndp=2):

        self.cif_path = cif_path
        self.chan_radius = chan_radius
        self.probe_radius = probe_radius
        self.num_samples = num_samples
        self.ndp = ndp

        self.pd, self.sa, self.pv = self.get_info()

        if any(x is not None for x in (self.pd, self.sa, self.pv)):
            self.prompt = self.process()
        else:
            self.prompt = None

    def get_info(self):
        try:
            pd = PoreDiameter(self.cif_path)
        except Exception:
            pd = None
        try:
            sa = SurfaceArea(self.cif_path, self.chan_radius,
                             self.probe_radius, self.num_samples)
        except Exception:
            sa = None
        try:
            pv = PoreVolume(self.cif_path, self.chan_radius,
                            self.probe_radius, self.num_samples)
        except Exception:
            pv = None
        return pd, sa, pv

    def _f(self, x):
        return f"{float(x):.{self.ndp}f}"

    @staticmethod
    def _join(items):
        if len(items) == 1:
            return items[0]
        return ", ".join(items[:-1]) + ", and " + items[-1]

    def process(self):
        sentences = []

        if self.pd is not None:
            sentences.append(
                f"The pore geometry is characterized by a largest cavity diameter (LCD) of {self._f(self.pd['LCD'])} Å "
                f"and a pore limiting diameter (PLD) of {self._f(self.pd['PLD'])} Å."
            )

        # probe radius 0 -> point-probe (geometric) values, not probe-accessible ones
        if self.probe_radius > 0:
            kind = "accessible"
            art = "an"
            probe_note = f" (probe radius {self.probe_radius:g} Å)"
        else:
            kind = "geometric"
            art = "a"
            probe_note = ""

        props = []
        if self.sa is not None:
            props.append(f"{art} {kind} surface area of {self._f(self.sa['ASA_m2_g'])} m²/g")
        if self.pv is not None:
            props.append(f"{art} {kind} void fraction of {self._f(self.pv['POAV_fraction'])}")
            props.append(f"{art} {kind} pore volume of {self._f(self.pv['POAV_cm3_g'])} cm³/g")
        if props:
            sentences.append(f"The framework has {self._join(props)}{probe_note}.")

        return " ".join(sentences)

    def __str__(self):
        return self.prompt or ""

    def __repr__(self):
        return f"prompt_5th(text={self.prompt!r})"
