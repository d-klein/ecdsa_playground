from ECC_01_plain_double_add import ecdsa, curve_affine
from Leakage import LeakageCollector
import matplotlib.pyplot as plt
import binascii
import hashlib
import gc


## Example 1: collect trace for plain double + add

# when running on a device, disable gc
# to get stable execution
# gc.disable()

# generate curve with NIST P256 curve params
curve = curve_affine.ECC()

# sample NIST ECDSA test vector. message is in plaintext. k fixed here
m = "5905238877c77421f73e43ee3da6f2d9e2ccad5fc942dcec0cbd25482935faaf416983fe165b1a045ee2bcd2e6dca3bdf46c4310a7461f9a37960ca672d3feb5473e253605fb1ddfd28065b53cb5858a8ad28175bf9bd386a5e471ea7a65c17cc934a9d791e91491eb3754d03799790fe2d308d16146d5c9b0d0debd97d79ce8"
d = 0x519b423d715f8b581f4fa8ee59f4771a5b44c8130b4e3eacca54a56dda72b464
k = 0x94a1bbb14b906a61a280f245f9e93c7f3b4a6247824f5d33b9670787642a68de

# hash message
m_hex = binascii.unhexlify(m)
hash_m = hashlib.sha256(m_hex).hexdigest()
l = int(hash_m, 16)

# setting leakage parameters
collector = LeakageCollector.LeakageCollector()
collector.doubleAmplitude = 20
collector.addAmplitude = 10
collector.signalRatio = 0.1

curve.generateLeakage = True
curve.collector = collector

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve)

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()


## Example 2: collect trace for projective coordinates
from ECC_02_projective_double_add import ecdsa, curve_projective
# generate curve with NIST P256 curve params
curve = curve_projective.ProECC()
curve.generateLeakage = True

collector.currentTrace = []
curve.collector = collector

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve)

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()

## Example 3: collect trace for comb method coordinates
from ECC_03_projective_double_alw_add_comb2 import ecdsa, curve_projective
# generate curve with NIST P256 curve params
curve = curve_projective.ProECC()
curve.generateLeakage = True

collector.currentTrace = []
curve.collector = collector

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve)

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()


## Example 4: collect trace for shamir-trick + naf representation
from ECC_04_projective_shamir import ecdsa, curve_projective
# generate curve with NIST P256 curve params
curve = curve_projective.ProECC()
curve.generateLeakage = True

collector.currentTrace = []
curve.collector = collector

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve, k_representation="naf")

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()


## Example 5: collect trace for shamir-trick + non-zero ternary representation
from ECC_04_projective_shamir import ecdsa, curve_projective
# generate curve with NIST P256 curve params
curve = curve_projective.ProECC()
curve.generateLeakage = True

collector.currentTrace = []
curve.collector = collector

# we use a value k where lsb == 1, otherwise this ternary representation without zeros
# does not work
m = "c5204b81ec0a4df5b7e9fda3dc245f98082ae7f4efe81998dcaa286bd4507ca840a53d21b01e904f55e38f78c3757d5a5a4a44b1d5d4e480be3afb5b394a5d2840af42b1b4083d40afbfe22d702f370d32dbfd392e128ea4724d66a3701da41ae2f03bb4d91bb946c7969404cb544f71eb7a49eb4c4ec55799bda1eb545143a7"
d = 0xb58f5211dff440626bb56d0ad483193d606cf21f36d9830543327292f4d25d8c
k = 0xe158bf4a2d19a99149d9cdb879294ccb7aaeae03d75ddd616ef8ae51a6dc1071

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve, k_representation="non_zero")

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()





## Example 5: collect trace for montgomery mult
from ECC_05_montgomery import ecdsa, curve_affine
# generate curve with NIST P256 curve params
curve = curve_affine.ECC()
curve.generateLeakage = True

collector.currentTrace = []
curve.collector = collector

# perform signature
rs = ecdsa.ecdsa(k, l, d, curve)

# plot result
trace = collector.currentTrace
plt.figure()
plt.plot(trace, linewidth=0.8)
plt.show()
