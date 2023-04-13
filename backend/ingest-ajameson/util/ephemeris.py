import re
import json


class Ephemeris:
    def __init__(self):
        self.ephem = {}
        self.jname = None
        self.p0 = 0
        self.dm = 0
        self.rm = 0
        self.configured = False

    def load_from_file(self, ephemeris_file):
        with open(ephemeris_file, "r") as file:
            data = file.read()
        self.load_from_string(data)

    def load_from_json(self, ephemeris_json):
        self.ephem = json.loads(ephemeris_json)
        self.parse()

    def load_from_string(self, ephemeris_string):
        lines = ephemeris_string.split("\n")
        for line in lines:
            line = line.strip()
            line = re.sub("#.*", "", line)
            if line:
                line = re.sub("\s+", " ", line)
                parts = line.split(" ", 2)
                if len(parts) < 2:
                    continue
                if len(parts) == 2:
                    self.set_val(parts[0], parts[1])
                else:
                    self.set_val_err(parts[0], parts[1], parts[2])
        self.parse()

    def parse(self):
        self.jname = self.get_val("PSRJ")
        _f0 = self.get_val("F0")
        _dm = self.get_val("DM")
        _rm = self.get_val("RM")
        if _f0 is not None:
            self.p0 = 1.0 / float(_f0)
        if _dm is not None:
            self.dm = float(_dm)
        if _rm is not None:
            self.rm = float(_rm)
        self.configured = True

    def set_val(self, key, val):
        self.ephem[key] = {"val": val}

    def set_val_err(self, key, val, err):
        self.ephem[key] = {"val": val, "err": err}

    def get(self, key):
        if key in self.ephem.keys():
            if "err" in self.ephem[key].keys():
                return (self.ephem[key]["val"], self.ephem[key]["err"])
            else:
                return self.ephem[key]["val"]
        else:
            return None

    def get_val(self, key):
        tup = self.get(key)
        val = None
        if tup is not None:
            val = tup[0]
        return val
