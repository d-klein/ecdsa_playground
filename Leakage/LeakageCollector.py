from random import randint

class LeakageCollector:
    def __init__(self):
        self.currentTrace = []
        self.time_unit = 10
        self.signalRatio = 0.1
        self.generateLeakage = False
        self.doubleAmplitude = 10
        self.addAmplitude = 20

    def int_to_bytelist_int(self,x):
        if x == 0:
            return [0]
        else:
            l = (x.bit_length() + 7) // 8 # min length of bytes required
            b = x.to_bytes(l, byteorder='little')
            return [ int(i) for i in b ]

    def resetTrace(self):
        self.currentTrace = []

    def addSignal(self, value, amplitude=20):
        #print(value)
        sig = self.int_to_bytelist_int(value)
        for i in sig:
            ran_i = randint(0, amplitude)
            sig_i = (amplitude * self.signalRatio) * (i / 255.)
            self.currentTrace.append(ran_i + sig_i)

