import matplotlib.pyplot as plt
from ecdsa import ECC
from ecdsa import ecdsa
import binascii
import hashlib
import gc

# when running on a device, disable gc
# to get stable execution
# gc.disable()

# generate curve with NIST P256 curve params
curve = ECC()

# sample NIST ECDSA test vector. message is in plaintext. k fixed here
m = "5905238877c77421f73e43ee3da6f2d9e2ccad5fc942dcec0cbd25482935faaf416983fe165b1a045ee2bcd2e6dca3bdf46c4310a7461f9a37960ca672d3feb5473e253605fb1ddfd28065b53cb5858a8ad28175bf9bd386a5e471ea7a65c17cc934a9d791e91491eb3754d03799790fe2d308d16146d5c9b0d0debd97d79ce8"
d = 0x519b423d715f8b581f4fa8ee59f4771a5b44c8130b4e3eacca54a56dda72b464
k = 0x94a1bbb14b906a61a280f245f9e93c7f3b4a6247824f5d33b9670787642a68de

# hash message
m_hex = binascii.unhexlify(m)
hash_m = hashlib.sha256(m_hex).hexdigest()
l = int(hash_m, 16)

# setting leakage parameters
curve.generateLeakage = True
curve.doubleAmplitude = 20
curve.addAmplitude = 10
curve.signalRatio = 0.1

# perform signature
rs = ecdsa(k, l, d, curve)

# plot result
trace = curve.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()