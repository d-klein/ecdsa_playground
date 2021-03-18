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
        self.generateLeakage = False
        self.collector = None

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
        checks if two points are equal
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
        Inverse of the point P on the elliptic curve y^2 = x^3 + ax + b.
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
            if (self.generateLeakage):
                self.collector.addSignal(P.x, self.collector.addAmplitude)
                self.collector.addSignal(P.y, self.collector.addAmplitude)
                self.collector.addSignal(Q.x, self.collector.addAmplitude)
                self.collector.addSignal(Q.y, self.collector.addAmplitude)
            t0 = (P.y * Q.z) % self.p
            t1 = (Q.y * P.z) % self.p
            u0 = (P.x * Q.z) % self.p
            u1 = (Q.x * P.z) % self.p
            if u0 == u1:
                if t0 == t1:
                    #print("doubling")
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
            if (self.generateLeakage):
                self.collector.addSignal(P.x, self.collector.doubleAmplitude)
                self.collector.addSignal(P.y, self.collector.doubleAmplitude)
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

    # given scalar k, get binary representation of k
    # split k in the middle to get to halves of size n,
    # and return a list of tuples k_i, k_(n+1) for i = 1..n
    def combBin(self, k):
        bins = [int(i) for i in bin(k)[2:]]
        #print(bins)
        if len(bins) % 2 != 0:
            bins.insert(0,0)
        # hardcoded: now increase up to 256 bit length
        l = len(bins)
        while(l < 256):
            bins.insert(0,0)
            l = len(bins)
        bins = bins[::-1]
        half = l//2
        firstHalf = bins[0:half]
        secondHalf = bins[half:]
        comb2 = list(zip(firstHalf, secondHalf))
        return comb2[::-1]

    def scalarMultBinary(self, k, P):

        # split k into two halfs k0 and k1
        # returns tupled binlist
        k_comb = self.combBin(k)

        # compute \lambda P
        # actually this should be done only once, for example
        # if P is the basepoint of the curve or if P is known
        # in other ways. Here we re-compute P for each scalar
        # multiplication, which is inefficient and should not be done
        # in a real implementation
        l_half = len(k_comb)
        lambdaP = P
        for i in range(0, l_half):
            lambdaP = self.double(lambdaP)

        # compute i*P + j*Q for all i,j values except (0,0)
        # in this straight forward representation
        # we use the binary representation of k, i.e. just with 0,1
        W_01 = lambdaP
        W_10 = P
        W_11 = self.add(P, lambdaP)

        R = None
        start_i = 0
        # find the first position where the combed-scalar
        # is not (0,0)
        u = None
        v = None
        for i in range(0, l_half):
            u,v = k_comb[i]
            if(not (u==0 and v==0)):
                start_i = i
                break
        if(u == 0 and v == 1):
            R = W_01
        if(u == 1 and v == 0):
            R = W_10
        if(u == 1 and v == 1):
            R = W_11

        for i in range(start_i+1, l_half):
            R = self.double(R)
            u, v = k_comb[i]
            if(u == 0 and v == 1):
                R = self.add(R, W_01)
            if (u == 1 and v == 0):
                R = self.add(R, W_10)
            if (u == 1 and v == 1):
                R = self.add(R, W_11)
        return R


    # given scalar k in ternary representation (0,1,-1)
    # split k in the middle to get to halves of size n,
    # and return a list of tuples k_i, k_(n+1) for i = 1..n
    def combNAF(self,k_naf):
        l = len(k_naf)
        half = l//2
        k_naf = k_naf[::-1]
        firstHalf = k_naf[0:half]
        secondHalf = k_naf[half:]
        comb2 = list(zip(firstHalf, secondHalf))
        return comb2[::-1]


    def scalarMultNAF(self, k, P):

        # split k into two halfs k0 and k1
        # returns tupled binlist
        k_comb = self.combNAF(k)

        # compute \lambda P
        # actually this should be done only once, for example
        # if P is the basepoint of the curve or if P is known
        # in other ways. Here we re-compute P for each scalar
        # multiplication, which is inefficient and should not be done
        # in a real implementation
        l_half = len(k_comb)
        lambdaP = P
        for i in range(0, l_half):
            lambdaP = self.double(lambdaP)

        # compute i*P + j*Q for all i,j values except (0,0)
        # here Q = \lambdaP
        # here we use the NAF representation of k, i.e. 0, 1 , -1
        # no W_00
        W_0p1 = lambdaP #
        W_0m1 = self.inv(lambdaP) #

        W_p10 = P #
        W_p1p1 = self.add(P, lambdaP) #
        W_p1m1 = self.add(P, self.inv(lambdaP))

        W_m10 = self.inv(P) #
        W_m1p1 = self.add(self.inv(P), lambdaP)
        W_m1m1 = self.add(self.inv(P), self.inv(lambdaP))

        R = None
        start_i = 0
        # find the first position where the combed-scalar
        # is not (0,0)
        u = None
        v = None
        for i in range(0, l_half):
            u,v = k_comb[i]
            if(not (u==0 and v==0)):
                start_i = i
                break
        if(u == 0 and v == 1):
            R = W_0p1
        if(u == 0 and v == -1):
            R = W_0m1
        if(u == 1 and v == 0):
            R = W_p10
        if (u == 1 and v == 1):
            R = W_p1p1
        if(u == 1 and v == -1):
            R = W_p1m1
        if(u == -1 and v == 0):
            R = W_m10
        if(u == -1 and v == 1):
            R = W_m1p1
        if (u == -1 and v == -1):
            R = W_m1m1

        for i in range(start_i+1, l_half):
            R = self.double(R)
            u, v = k_comb[i]
            if (u == 0 and v == 1):
                R = self.add(R, W_0p1)
            if (u == 0 and v == -1):
                R = self.add(R, W_0m1)
            if (u == 1 and v == 0):
                R = self.add(R, W_p10)
            if (u == 1 and v == 1):
                R = self.add(R, W_p1p1)
            if (u == 1 and v == -1):
                R = self.add(R, W_p1m1)
            if (u == -1 and v == 0):
                R = self.add(R, W_m10)
            if (u == -1 and v == 1):
                R = self.add(R, W_m1p1)
            if (u == -1 and v == -1):
                R = self.add(R, W_m1m1)
        return R