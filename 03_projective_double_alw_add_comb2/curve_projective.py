from collections import namedtuple
from random import randint

Point = namedtuple("Point", ["x", "y"])
ProPoint = namedtuple("ProPoint", ["x", "y", "z"])

# point at infinity
O_POINT_INF = 'PointInfty'

class ProECC:
    def __init__(self):
        """
        creates an ECC object for EC arithmetic
        Curve NIST P256 is initialized as default
        """
        # nist 256 as default
        self.p = 115792089210356248762697446949407573530086143415290314195533631308867097853951
        self.a = -3
        self.b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
        self.n = 115792089210356248762697446949407573529996955224135760342422259061068512044369
        basePoint= Point(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
                              0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
        self.proBasePoint = ProPoint(basePoint.x, basePoint.y, 1)  #None #0 #self.aff2pro(self.basePoint) todo: better initialization/sanity check here
        self.currentTrace = []
        self.time_unit = 10
        self.signalRatio = 0.1
        self.generateLeakage = False
        self.doubleAmplitude = 10
        self.addAmplitude = 20

    def aff2pro(self, affPoint, z):
        assert(z != 0)
        if(affPoint == O_POINT_INF):
            return O_POINT_INF
        else:
            return ProPoint((affPoint.x * z) % self.p, (affPoint.y * z) % self.p, z)

    def pro2aff(self, proPoint):
        assert(proPoint.x >= 0)
        assert(proPoint.y <= self.p)
        if (proPoint == O_POINT_INF):
            return O_POINT_INF
        else:
            div = self.inv_mod(proPoint.z, self.p)
            return Point((proPoint.x * div) % self.p, (proPoint.y * div) % self.p)

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
        sig = self.int_to_bytelist_int(value)
        for i in sig:
            ran_i = randint(0, amplitude)
            sig_i = (amplitude * self.signalRatio) * (i / 255.)
            self.currentTrace.append(ran_i + sig_i)

    def setCurveParameters(self, a, b, p, n, basePoint):
        """
        sets custom curve parameter
        :param a: coefficient a
        :param b: coefficient b
        :param p: prime modulus p
        :param n: order n
        :param basePoint: base point with coordinates G_x, G_y
        """
        self.a = a
        self.b = b
        self.p = p
        self.n = n
        self.basePoint = basePoint
        self.proBasePoint = self.aff2pro(self.basePoint)
        assert(self.onCurve(basePoint))

    def onCurve(self,P):
        """
        checks if the projective point P is on the curve
        :param P:
        :return: True, if the point is on the curve, False otherwise
        """
        if P == O_POINT_INF:
            return True
        else:
            affP = self.pro2aff(P)
            # check if P is reduced, otherwise setting into
            # equation might give strange results
            if (affP.x < 0 or affP.x >= self.p):
                return False
            if (affP.y < 0 or affP.y >= self.p):
                return False
            eval = (  ((affP.y ** 2) % self.p) - (((affP.x ** 3) % self.p) + ((self.a * affP.x)%self.p) + self.b)) % self.p
            if (eval == 0):
                return True
            else:
                return False

    def inv_mod(self, value, modulus):
        if value == 0:
            raise ValueError("Division by zero")
        # if value < 0, add prime
        if(value < 0):
            value += self.p
        # Extended Euclidean algorithm
        x, y = modulus, value
        a, b = 0, 1
        while y != 0:
            a, b = b, a - x // y * b
            x, y = y, x % y
        if x == 1:
            return a
        else:
            raise ValueError("Value and modulus not coprime")

    def isEqual(self, P, Q):
        """
        checks if two projective points are equal
        :param P: point 1
        :param Q: point 2
        :return: true, if x,y coordinates match
        """
        if(P == O_POINT_INF):
            return (Q == O_POINT_INF)
        if(Q == O_POINT_INF):
            return (P == O_POINT_INF)
        affP = self.pro2aff(P)
        affQ = self.pro2aff(Q)
        return (affP.x == affQ.x and affP.y == affQ.y)


    def inv(self,P):
        """
        Inverse of the (projective) point P on the elliptic curve y^2 = x^3 + ax + b.
        :return: inverse point
        """
        if P == O_POINT_INF:
            return P
        return ProPoint(P.x, (-P.y) % self.p, P.z)

    # P + Q for projective coordinates
    def add(self, P, Q):
        if not (self.onCurve(P) and self.onCurve(Q)):
            raise ValueError("Invalid inputs")
        # check for point at infty
        if P == O_POINT_INF:
            result = Q
        elif Q == O_POINT_INF:
            result = P
        elif Q == self.inv(P):
            result = O_POINT_INF
        else:
            t0 = (P.y * Q.z) % self.p
            t1 = (Q.y * P.z) % self.p
            u0 = (P.x * Q.z) % self.p
            u1 = (Q.x * P.z) % self.p
            if u0 == u1:
                if t0 == t1:
                    print("doubling")
                    result = self.double(P)
                else:
                    result = O_POINT_INF
            else:
                t = (t0 - t1) % self.p
                u = (u0 - u1) % self.p
                u2 = (u * u) % self.p
                v = (P.z * Q.z) % self.p
                w = ((t * t * v) % self.p ) - ((u2 * ((u0 + u1) % self.p) ) % self.p)
                u3 = (u * u2) % self.p
                rx = (u * w) % self.p
                ry = (((t * ((((u0 * u2) % self.p) - w)% self.p)) % self.p) - ((t0 * u3) % self.p)) % self.p
                rz = (u3 * v) % self.p
                result = ProPoint(rx, ry, rz)
        assert self.onCurve(result)
        return result

    def double(self,P):
        """
        doubles the projective EC point P
        :param P: EC Point
        :return: 2*P
        """
        if not self.onCurve(P):
            raise ValueError("Invalid inputs")
        # check for point at infty
        if P == O_POINT_INF:
            return O_POINT_INF
        if P.y == 0:
            return O_POINT_INF
        else:
            t = ((P.x * P.x * 3) % self.p) + ((self.a * P.z * P.z) % self.p)
            u = (P.y * P.z * 2) % self.p
            v = (u * P.x * P.y * 2) % self.p
            w = (((t * t) % self.p) - ((v * 2) % self.p)) % self.p
            rx = (u * w) % self.p
            ry = (((t * ((v - w) % self.p)) % self.p) - ((u * u * P.y * P.y * 2) % self.p)) % self.p
            rz = (u * u * u) % self.p
            result = ProPoint(rx, ry, rz)
        assert self.onCurve(result)
        return result

    def comb2(self,k):
        bins = [int(i) for i in bin(k)[2:]]
        if len(bins) % 2 != 0:
            bins.insert(0,0)
        # hardcoded: now increase up to 258 bit length
        l = len(bins)
        #while(l < 256):
        #    bins.insert(0,0)
        #    l = len(bins)
        #print("len: " + str(len(bins)))
        half = l//2
        firstHalf = bins[0:half]
        secondHalf = bins[half:]
        comb2 = list(zip(firstHalf, secondHalf))
        comb2 = [2 * i + j for (i, j) in comb2]
        return comb2

    def comb2_258(self,k):
        bins = [int(i) for i in bin(k)[2:]]
        if len(bins) % 2 != 0:
            bins.insert(0,0)
        # hardcoded: now increase up to 258 bit length
        l = len(bins)
        while(l < 258):
            bins.insert(0,0)
            l = len(bins)
        #print("len: " + str(len(bins)))
        half = l//2
        firstHalf = bins[0:half]
        secondHalf = bins[half:]
        comb2 = list(zip(firstHalf, secondHalf))
        comb2 = [2 * i + j for (i, j) in comb2]
        return comb2

    def scalarMultComb2Unmasked(self, k, P):
        """
        scalar multiplication k*P on current curve
        computation similar to description of "A side journey into open titan", section 2.3.1
        (signature verification algorithm)

        :param k: scalar
        :param P: EC point P
        :return: k*P
        """

        k_comb = self.comb2(k)
        lk_2 = len(k_comb)

        P2 = P
        for i in range(0, lk_2):
            P2 = self.double(P2)

        P3 = self.add(P, P2)

        PP = [ None, P, P2, P3]

        S = O_POINT_INF
        first_non_null = 0
        for l in range(0, lk_2):
            if(k_comb[l] != 0):
                first_non_null = l
                break
        for i in range(first_non_null, lk_2):
            S = self.double(S)
            if(k_comb[i] > 0):
                S = self.add(S, PP[k_comb[i]])
        return S

    def scalarMultComb2Masked(self, k, P, G0_idx):
        """
        scalar multiplication k*P on current curve
        computation similar to description of "A side journey into open titan", section 2.3.3
        (signature _creation_ algorithm)

        :param k: scalar
        :param P: EC point P
        :param G0_idx: index indicating whether G1 (idx0) ... G4 (idx3) should be taken as random point G0
        :return: k*P
        """

        k_comb = self.comb2_258(k)

        G1 = P
        G4 = G1
        for i in range(0, 128):
            G4 = self.double(G4)
        G2 = self.double(G4)
        G3 = self.add(G1,G2)

        PP = [ G1, G2, G3, G4]
        G0 = PP[G0_idx]
        PP.insert(0, G0)

        S = G1
        Dummy = None
        for i in range(1,129):
            S = self.double(S)
            if(k_comb[i] > 0):
                S = self.add(S, PP[k_comb[i]])
            else:
                Dummy = self.add(S, PP[0])
        if(k_comb[0] == 0):
            S = self.add(S, self.inv(PP[4]))
        else:
            Dummy = self.add(S, self.inv(PP[4]))

        return S

"""
        # G1 is the basepoint
        G1 = self.proBasePoint
        # G4 = [2^128]*G1 (use doubling for that)
        G4 = G1
        for i in range(0,lk_2):
            G4 = self.double(G4)
        # G2 is [2^129]G1 = 2*G4
        G2 = self.double(G4)
        G3 = self.add(G1,G2)
        precomputedPoints = [G1, G2, G3, G4]
        # for G0 we take randomly one of the precomputed points
        G0 = precomputedPoints[G0_idx]

        precomputedPoints.insert(0, G0)
"""

"""
        S = G1
        Dummy = None

        print("precomputed points")
        for i in range(0,5):
            print(i)
            print(precomputedPoints[i])

        for i in range(0, len(k_comb)):
            S = self.double(S)
            ki = k_comb[i]
            #print(ki)
            if(ki > 0):
                S = self.add(S, precomputedPoints[ki])
        return S
"""

"""
        for i in range(1, 129):
            S = self.double(S)
            ki = k_comb[i]
            if(ki > 0):
                S = self.add(S, precomputedPoints[ki])
            else:
                Dummy = self.add(S, precomputedPoints[0])
        if(precomputedPoints[0] == 0):
            S = self.add(S, self.inv(precomputedPoints[4]))
        else:
            Dummy = self.add(S, self.inv(precomputedPoints[4]))
        return S
"""