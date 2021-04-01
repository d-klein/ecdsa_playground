from .curve_affine import Point, ECC, O_POINT_INF

class TestECC():

    # all tests here are on the default (Nist P-256) curve
    def testAdditions(self):
        ecc = ECC()

        # bp + O
        point1 = ecc.basePoint
        pointBp = Point(0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
                        0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)
        assert(ecc.isEqual(ecc.add(point1, O_POINT_INF), pointBp))

        # bp + bp
        point1 = ecc.basePoint
        point2 = ecc.basePoint
        point2Bp = Point(0x7CF27B188D034F7E8A52380304B51AC3C08969E277F21B35A60B48FC47669978,
                         0x07775510DB8ED040293D9AC69F7430DBBA7DADE63CE982299E04B79D227873D1)
        assert (ecc.isEqual(ecc.add(point1, point2), point2Bp))

        # bp + bp + bp
        point1 = ecc.basePoint
        point2 = point2Bp
        point3Bp = Point(0x5ECBE4D1A6330A44C8F7EF951D4BF165E6C6B721EFADA985FB41661BC6E7FD6C,
                         0x8734640C4998FF7E374B06CE1A64A2ECD82AB036384FB83D9A79B127A27D5032)
        assert (ecc.isEqual(ecc.add(point1, point2), point3Bp))

        # bp + bp + bp + bp
        point1 = ecc.basePoint
        point2 = point3Bp
        point4Bp = Point(0xE2534A3532D08FBBA02DDE659EE62BD0031FE2DB785596EF509302446B030852,
                         0xE0F1575A4C633CC719DFEE5FDA862D764EFC96C3F30EE0055C42C23F184ED8C6)
        assert (ecc.isEqual(ecc.add(point1, point2), point4Bp))

    def testScalarMultiplication(self):


        ecc = ECC()
        # compute 4 * bp

        BP4 = ecc.scalarMultMG(4, ecc.basePoint)
        pointRes = Point(0xE2534A3532D08FBBA02DDE659EE62BD0031FE2DB785596EF509302446B030852,
                         0xE0F1575A4C633CC719DFEE5FDA862D764EFC96C3F30EE0055C42C23F184ED8C6)
        #print("desired result")
        #print(pointRes)
        assert(ecc.isEqual(pointRes, BP4))


        ecc = ECC()
        # compute 5 * bp

        BP5 = ecc.scalarMultMG(5, ecc.basePoint)

        pointRes = Point(0x51590B7A515140D2D784C85608668FDFEF8C82FD1F5BE52421554A0DC3D033ED,
                         0xE0C17DA8904A727D8AE1BF36BF8A79260D012F00D4D80888D1D0BB44FDA16DA4)
        #print("desired result")
        #print(pointRes)
        assert(ecc.isEqual(pointRes, BP5))


        ecc = ECC()
        # compute n * bp

        BPmul = ecc.scalarMultMG(112233445566778899, ecc.basePoint)
        pointRes = Point(0x339150844EC15234807FE862A86BE77977DBFB3AE3D96F4C22795513AEAAB82F,
                         0xB1C14DDFDC8EC1B2583F51E85A5EB3A155840F2034730E9B5ADA38B674336A21)
        assert(ecc.isEqual(pointRes, BPmul))

        ecc = ECC()
        # compute n * bp
        BPmul = ecc.scalarMultMG(29852220098221261079183923314599206100666902414330245206392788703677545185283, ecc.basePoint)
        pointRes = Point(0x9EACE8F4B071E677C5350B02F2BB2B384AAE89D58AA72CA97A170572E0FB222F,
                         0x1BBDAEC2430B09B93F7CB08678636CE12EAAFD58390699B5FD2F6E1188FC2A78)
        assert(ecc.isEqual(pointRes, BPmul))


    def testScalarMultiplicationVecs(self):
        k=None
        x=None
        y=None
        with open("../testvecs_p256.txt", "r") as f:
            for line in f:
                if(k!= None and x!= None and y!= None):
                    # do computation
                    ecc = ECC()
                    BPMul = ecc.scalarMultMG(k, ecc.basePoint)
                    pointRes = Point(x,y)
                    assert (ecc.isEqual(pointRes, BPMul))
                    k = x = y = None
                var_val = line.split("=")
                if (len(var_val) == 2):
                    var = var_val[0].strip()
                    val = var_val[1].strip()
                    if (var == "k"):
                        k = int(val)
                    if(var == "x"):
                        x = int(val, 16)
                    if(var == "y"):
                        y = int(val, 16)


tester = TestECC()
tester.testScalarMultiplication()
tester.testScalarMultiplicationVecs()