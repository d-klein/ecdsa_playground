from .curve_projective import Point, ProECC, O_POINT_INF
from .ecdsa import ecdsa
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
    #Msg = c5204b81ec0a4df5b7e9fda3dc245f98082ae7f4efe81998dcaa286bd4507ca840a53d21b01e904f55e38f78c3757d5a5a4a44b1d5d4e480be3afb5b394a5d2840af42b1b4083d40afbfe22d702f370d32dbfd392e128ea4724d66a3701da41ae2f03bb4d91bb946c7969404cb544f71eb7a49eb4c4ec55799bda1eb545143a7
    #d = b58f5211dff440626bb56d0ad483193d606cf21f36d9830543327292f4d25d8c
    #Qx = 68229b48c2fe19d3db034e4c15077eb7471a66031f28a980821873915298ba76
    #Qy = 303e8ee3742a893f78b810991da697083dd8f11128c47651c27a56740a80c24c
    #k = e158bf4a2d19a99149d9cdb879294ccb7aaeae03d75ddd616ef8ae51a6dc1071
    #R = e67a9717ccf96841489d6541f4f6adb12d17b59a6bef847b6183b8fcf16a32eb
    #S = 9ae6ba6d637706849a6a9fc388cf0232d85c26ea0d1fe7437adb48de58364333


    def testSigGeneration(self):
        curve = ProECC()

        # create test vector
        # m: message
        # d: private key
        # k: random nonce
        # test with NAF representation
        m = "c5204b81ec0a4df5b7e9fda3dc245f98082ae7f4efe81998dcaa286bd4507ca840a53d21b01e904f55e38f78c3757d5a5a4a44b1d5d4e480be3afb5b394a5d2840af42b1b4083d40afbfe22d702f370d32dbfd392e128ea4724d66a3701da41ae2f03bb4d91bb946c7969404cb544f71eb7a49eb4c4ec55799bda1eb545143a7"
        d = 0xb58f5211dff440626bb56d0ad483193d606cf21f36d9830543327292f4d25d8c
        k = 0xe158bf4a2d19a99149d9cdb879294ccb7aaeae03d75ddd616ef8ae51a6dc1071

        m_hex = binascii.unhexlify(m)
        hash_m = hashlib.sha256(m_hex).hexdigest()
        l = int(hash_m, 16)

        rs = ecdsa(k, l, d, curve, k_representation="naf")

        pointResult = Point(0xe67a9717ccf96841489d6541f4f6adb12d17b59a6bef847b6183b8fcf16a32eb,
                            0x9ae6ba6d637706849a6a9fc388cf0232d85c26ea0d1fe7437adb48de58364333)

        print("result should be: ")
        print(hex(pointResult.x))
        print(hex(pointResult.y))
        print("r,s, computed:")
        print(hex(rs.x))
        print(hex(rs.y))
        assert(curve.isEqual(curve.aff2pro(pointResult,1), curve.aff2pro(rs,1)))


        curve = ProECC()

        # create test vector
        # m: message
        # d: private key
        # k: random nonce
        # test with NAF representation
        m = "c5204b81ec0a4df5b7e9fda3dc245f98082ae7f4efe81998dcaa286bd4507ca840a53d21b01e904f55e38f78c3757d5a5a4a44b1d5d4e480be3afb5b394a5d2840af42b1b4083d40afbfe22d702f370d32dbfd392e128ea4724d66a3701da41ae2f03bb4d91bb946c7969404cb544f71eb7a49eb4c4ec55799bda1eb545143a7"
        d = 0xb58f5211dff440626bb56d0ad483193d606cf21f36d9830543327292f4d25d8c
        k = 0xe158bf4a2d19a99149d9cdb879294ccb7aaeae03d75ddd616ef8ae51a6dc1071

        m_hex = binascii.unhexlify(m)
        hash_m = hashlib.sha256(m_hex).hexdigest()
        l = int(hash_m, 16)

        rs = ecdsa(k, l, d, curve, k_representation="non_zero")

        pointResult = Point(0xe67a9717ccf96841489d6541f4f6adb12d17b59a6bef847b6183b8fcf16a32eb,
                            0x9ae6ba6d637706849a6a9fc388cf0232d85c26ea0d1fe7437adb48de58364333)

        print("result should be: ")
        print(hex(pointResult.x))
        print(hex(pointResult.y))
        print("r,s, computed:")
        print(hex(rs.x))
        print(hex(rs.y))
        assert(curve.isEqual(curve.aff2pro(pointResult,1), curve.aff2pro(rs,1)))


tester = TestECDSA()
tester.testSigGeneration()