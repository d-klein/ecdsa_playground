from .curve_projective import Point

## ecdsa with base point blinding by using projective coordinates
##
##  randomly generate z
##  project coordinates to (xz,yz,z)
##  perform scalar multiplication (optimized)
##  get r := x/z mod p
##  compute s as normal

def ecdsa(k, m, d, ecc_curve_projective):
    k = k % ecc_curve_projective.n
    Q = ecc_curve_projective.scalarMult(k, ecc_curve_projective.proBasePoint)
    affQ = ecc_curve_projective.pro2aff(Q)
    r = affQ.x
    if (r == 0):
        raise ValueError("ecdsa_k: r == 0!")
    kinv = ecc_curve_projective.inv_mod(k, ecc_curve_projective.n)
    s = (kinv * ((m + ((r * d)% ecc_curve_projective.n)) % ecc_curve_projective.n)) % ecc_curve_projective.n
    if (s == 0):
        raise ValueError("ecdsa_k: s == 0!")
    return Point(r, s)
