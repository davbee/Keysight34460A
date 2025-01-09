import pyvisa


class KS34460A:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.dmm = self.rm.list_resources()[0]
        self.inst = self.rm.open_resource(self.dmm)

    def close(self):
        self.inst.close()
