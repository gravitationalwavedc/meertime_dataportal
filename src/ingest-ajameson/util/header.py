import re
import json


class KeyValueStore:
    def __init__(self, fname):
        self.cfg = {}
        self.read_file(fname)

    def read_file(self, fname):
        fptr = open(fname, 'r')
        for line in fptr:
            # remove all comments
            line = line.strip()
            line = re.sub("#.*", "", line)
            if line:
                line = re.sub("\s+", " ", line)
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    self.cfg[parts[0]] = parts[1].strip()
        fptr.close()

    def set(self, key, value):
        self.cfg[key] = str(value)

    def get(self, key):
        if key in self.cfg.keys():
            return self.cfg[key]
        else:
            return "None"


class Header(KeyValueStore):
    def __init__(self, fname):
        KeyValueStore.__init__(self, fname)

    def parse(self):
        self.source = self.cfg["SOURCE"]
        self.ra = self.cfg["RA"]
        self.dec = self.cfg["DEC"]
        self.tied_beam_ra = self.cfg["TIED_BEAM_RA"]
        self.tied_beam_dec = self.cfg["TIED_BEAM_DEC"]
        self.telescope = self.cfg["TELESCOPE"]

        # Instrument Config
        self.bandwidth = float(self.cfg["BW"])
        self.frequency = float(self.cfg["FREQ"])
        self.nchan = int(self.cfg["NCHAN"])
        self.npol = int(self.cfg["NPOL"])
        self.beam = self.cfg["BEAM"]


class PTUSEHeader(Header):
    def __init__(self, fname):
        Header.__init__(self, fname)

    def parse(self):
        Header.parse(self)

        self.proposal_id = self.get("PROPOSAL_ID")
        self.schedule_block_id = self.get("SCHEDULE_BLOCK_ID")
        self.experiment_id = self.get("EXPERIMENT_ID")
        self.phaseup_id = self.get("PHASEUP_ID")
        self.delaycal_id = self.get("DELCAY_ID")
        self.nant = len(self.get("ANTENNAE").split(","))

        h_weights = self.get("WEIGHTS_POLH").split(",")
        v_weights = self.get("WEIGHTS_POLV").split(",")
        polh = 0
        polv = 0
        for w in h_weights:
            polh += float(w)
        for w in v_weights:
            polv += float(w)
        nant_eff_h = polh / len(h_weights)
        nant_eff_v = polh / len(v_weights)
        self.nant_eff = int((nant_eff_h + nant_eff_v) / 2)
        self.configuration = json.dumps(self.cfg)

        self.machine = "PTUSE"
        self.machine_version = "1.0"
        self.machine_config = "{}"

        self.fold_dm = float(self.get("FOLD_DM"))
        self.fold_nchan = int(self.get("FOLD_OUTNCHAN"))
        self.fold_npol = int(self.get("FOLD_OUTNPOL"))
        self.fold_nbin = int(self.get("FOLD_OUTNBIN"))
        self.fold_tsubint = int(self.get("FOLD_OUTTSUBINT"))
