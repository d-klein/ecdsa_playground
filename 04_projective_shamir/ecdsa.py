from curve_projective import Point
from naf import make_non_zero, extend_non_zero, make_naf, extend_naf, undo_naf

## ecdsa with base point blinding and double & add by using projective coordinates
##
##  randomly generate z
##  project coordinates to (xz,yz,z)
##  perform scalar multiplication (optimized)
##  get r := x/z mod p
##  compute s as normal

def ecdsa(k, m, d, ecc_curve_projective, k_representation="naf"):
    k = k % ecc_curve_projective.n
    k_bins = None
    if(k_representation == "naf"):
        print("NAF")
        k_nz = make_naf(k)
        # if len of naf representation is below 256, we extend it accordingly
        # otherwise we extend it to an even length by prepending zeros
        if (len(k_nz) < 256):
            k_bins = extend_naf(k_nz, 256)
        else:
            if (len(k_nz) % 2 != 0):
                k_bins = k_nz
                k_bins.insert(0, 0)
    elif(k_representation == "non_zero"):
        print("NON ZERO")
        k_nz = make_non_zero(k)
        if(len(k_nz) > 256):
            raise ValueError("unable to create non-zero representation of k with length <= 256")
        k_bins = extend_non_zero(k_nz, 256)
    Q = ecc_curve_projective.scalarMultNAF(k_bins, ecc_curve_projective.proBasePoint)
    affQ = ecc_curve_projective.pro2aff(Q)
    r = affQ.x
    if (r == 0):
        raise ValueError("ecdsa_k: r == 0!")
    kinv = ecc_curve_projective.inv_mod(k, ecc_curve_projective.n)
    s = (kinv * ((m + ((r * d)% ecc_curve_projective.n)) % ecc_curve_projective.n)) % ecc_curve_projective.n
    if (s == 0):
        raise ValueError("ecdsa_k: s == 0!")
    return Point(r, s)
