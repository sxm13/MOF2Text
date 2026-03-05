from mof2text.topology.runner import get_topo


class prompt_2nd():

    def __init__(self, cif_path):
        self.cif_path = cif_path
        self.results = self.mof_analyze()
        if self.results is not None:
            self.prompt = self.process()
        else:
            self.prompt = None


    def mof_analyze(self):
        try:
            results = get_topo(self.cif_path)
        except:
            results = None
        return results


    def process(self):
        if self.results['catenation'][0] > 1:
            text_ = f"This interpenetrated "
        else:
            text_ = f"This non-interpenetrated "
        text_ += f"{self.results['dimension'][0]}d framework with the {self.results['topology'][0]} topology"
        return text_.rstrip()


    def __str__(self):
        return self.prompt or ""


    def __repr__(self):
        return f"prompt_2nd(text={self.prompt!r})"