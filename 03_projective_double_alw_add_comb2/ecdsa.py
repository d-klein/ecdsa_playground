from curve_projective import Point

## ecdsa with base point blinding and double & add by using projective coordinates
##
##  randomly generate z
##  project coordinates to (xz,yz,z)
##  perform scalar multiplication (optimized)
##  get r := x/z mod p
##  compute s as normal

def ecdsa(k, m, d, ecc_curve_projective):
    k = k % ecc_curve_projective.n
    # we need a random point for the dummy add operation
    # here we simply take G1, i.e. one point that needs
    # to be precomputed for the comb2 scalar multiplication anyway
    random_point_idx = 0
    Q = ecc_curve_projective.scalarMultComb2Masked(k, ecc_curve_projective.proBasePoint, random_point_idx)
    affQ = ecc_curve_projective.pro2aff(Q)
    r = affQ.x
    if (r == 0):
        raise ValueError("ecdsa_k: r == 0!")
    kinv = ecc_curve_projective.inv_mod(k, ecc_curve_projective.n)
    s = (kinv * ((m + ((r * d)% ecc_curve_projective.n)) % ecc_curve_projective.n)) % ecc_curve_projective.n
    if (s == 0):
        raise ValueError("ecdsa_k: s == 0!")
    return Point(r, s)
