from curve_projective import Point, ProECC, O_POINT_INF
from ecdsa import ecdsa
import hashlib
import binascii

class TestECDSA():

    # all tests here are on the default (Nist P-256) curve
    # NIST test vector.
    # Msg: message
    # d: private key
    # Qx, Qy: public key (point)
    # k : nonce
    # R,S : signature (point)
    # Msg = 5905238877c77421f73e43ee3da6f2d9e2ccad5fc942dcec0cbd25482935faaf416983fe165b1a045ee2bcd2e6dca3bdf46c4310a7461f9a37960ca672d3feb5473e253605fb1ddfd28065b53cb5858a8ad28175bf9bd386a5e471ea7a65c17cc934a9d791e91491eb3754d03799790fe2d308d16146d5c9b0d0debd97d79ce8
    # d = 519b423d715f8b581f4fa8ee59f4771a5b44c8130b4e3eacca54a56dda72b464
    # Qx = 1ccbe91c075fc7f4f033bfa248db8fccd3565de94bbfb12f3c59ff46c271bf83
    # Qy = ce4014c68811f9a21a1fdb2c0e6113e06db7ca93b7404e78dc7ccd5ca89a4ca9
    # k = 94a1bbb14b906a61a280f245f9e93c7f3b4a6247824f5d33b9670787642a68de
    # R = f3ac8061b514795b8843e3d6629527ed2afd6b1f6a555a7acabb5e6f79c8c2ac
    # S = 8bf77819ca05a6b2786c76262bf7371cef97b218e96f175a3ccdda2acc058903
    def testSigGeneration(self):
        curve = ProECC()

        # create test vector
        # m: message
        # d: private key
        # k: random nonce
        m = "5905238877c77421f73e43ee3da6f2d9e2ccad5fc942dcec0cbd25482935faaf416983fe165b1a045ee2bcd2e6dca3bdf46c4310a7461f9a37960ca672d3feb5473e253605fb1ddfd28065b53cb5858a8ad28175bf9bd386a5e471ea7a65c17cc934a9d791e91491eb3754d03799790fe2d308d16146d5c9b0d0debd97d79ce8"
        d = 0x519b423d715f8b581f4fa8ee59f4771a5b44c8130b4e3eacca54a56dda72b464
        k = 0x94a1bbb14b906a61a280f245f9e93c7f3b4a6247824f5d33b9670787642a68de

        m_hex = binascii.unhexlify(m)
        hash_m = hashlib.sha256(m_hex).hexdigest()
        l = int(hash_m, 16)

        rs = ecdsa(k, l, d, curve)

        pointResult = Point(0xf3ac8061b514795b8843e3d6629527ed2afd6b1f6a555a7acabb5e6f79c8c2ac,
                            0x8bf77819ca05a6b2786c76262bf7371cef97b218e96f175a3ccdda2acc058903)

        assert(curve.isEqual(curve.aff2pro(pointResult,1), curve.aff2pro(rs,1)))
