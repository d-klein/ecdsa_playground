from collections import namedtuple
from random import randint

## standard double + add without countermeasures
Point = namedtuple("Point", ["x", "y"])

# point at infinity
O_POINT_INF = 'PointInfty'

class ECC:
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
        self.basePoint= Point(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
                              0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5)
        self.collector = None
        self.generateLeakage = False

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
        assert(self.onCurve(basePoint))

    def onCurve(self,P):
        """
        checks if the point P is on the curve
        :param P:
        :return: True, if the point is on the curve, False otherwise
        """
        if P == O_POINT_INF:
            return True
        else:
            # check if P is reduced, otherwise setting into
            # equation might give strange results
            if (P.x < 0 or P.x >= self.p):
                return False
            if (P.y < 0 or P.y >= self.p):
                return False
            eval = (P.y ** 2 - (P.x ** 3 + self.a * P.x + self.b)) % self.p
            if (eval == 0):
                return True
            else:
                return False

 #   def inv_mod_p(self,x):
 #       """
 #       computes x^{-1} mod p
 #       :param x:
 #       :return: x^{-1} mod p. raises ZeroDivisionError if inversion is impossible
 #       """
 #       if x % self.p == 0:
 #           raise ZeroDivisionError("Impossible inverse")
 #       if(x < 0):
 #           x += self.p
 #       return pow(x, self.p - 2, self.p)

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

#    def inv_mod_n(self,x):
#        """
#        computes x^{-1} mod n
#        :param x:
#        :return: x^{-1} mod n. raises ZeroDivisionError if inversion is impossible
#        """
#        if x % self.n == 0:
#            raise ZeroDivisionError("Impossible inverse")
#        return pow(x, self.n - 2, self.n)


    def isEqual(self, P, Q):
        """
        checks if two points are equal
        :param P: point 1
        :param Q: point 2
        :return: true, if P.x == Q.x and P.y == Q.y
        """
        if(P == O_POINT_INF):
            return (Q == O_POINT_INF)
        if(Q == O_POINT_INF):
            return (P == O_POINT_INF)
        return (P.x == Q.x and P.y == Q.y)


    def inv(self,P):
        """
        Inverse of the point P on the elliptic curve y^2 = x^3 + ax + b.
        :return: inverse point
        """
        if P == O_POINT_INF:
            return P
        return Point(P.x, (-P.y) % self.p)

    # P + Q
    def add(self, P, Q):
        """
        computes P+Q on the current curve
        :param P: EC point P
        :param Q:  EC point Q
        :return: P+Q
        """
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
            # general case
            if(self.generateLeakage):
                self.collector.addSignal(P.x, self.collector.addAmplitude)
                self.collector.addSignal(P.y, self.collector.addAmplitude)
                self.collector.addSignal(Q.x, self.collector.addAmplitude)
                self.collector.addSignal(Q.y, self.collector.addAmplitude)
            if P == Q:
                dydx = (3 * P.x**2 + self.a) * self.inv_mod(2 * P.y, self.p)
            else:
                dydx = (Q.y - P.y) * self.inv_mod(Q.x - P.x, self.p)
            x = (dydx**2 - P.x - Q.x) % self.p
            y = (dydx * (P.x - x) - P.y) % self.p
            result = Point(x, y)

        # The above computations *should* have given us another point
        # on the curve.
        assert self.onCurve(result)
        return result

    def double(self,P):
        """
        doubles the EC point P
        :param P: EC Point
        :return: 2*P
        """
        if not self.onCurve(P):
            raise ValueError("Invalid inputs")
        # check for point at infty
        if P == O_POINT_INF:
            return O_POINT_INF
        else:
            if(self.generateLeakage):
                self.collector.addSignal(P.x, self.collector.doubleAmplitude)
                self.collector.addSignal(P.y, self.collector.doubleAmplitude)
            dydx = (3 * P.x**2 + self.a) * self.inv_mod(2 * P.y, self.p)
            x = (dydx ** 2 - (2*P.x)) % self.p
            y = (dydx * (P.x - x) - P.y) % self.p
            result = Point(x, y)
        assert self.onCurve(result)
        return result

    def scalarMult(self, k, P):
        """
        scalar multiplication k*P on current curve; naive/non-secure

        :param k: scalar
        :param P: EC point P
        :return: k*P
        """
        k_bin = bin(k)[2:]
        Q = 'PointInfty'
        for i in (range(0, len(k_bin))):
            Q = self.double(Q)
            if (k_bin[i] == '1'):
                Q = self.add(Q, P)
        return Q