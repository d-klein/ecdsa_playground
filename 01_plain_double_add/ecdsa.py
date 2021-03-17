from curve_affine import ECC, Point, O_POINT_INF

def ecdsa(k, m, d, ecc_curve_affine):
    """
    computes an ecdsa signature
    :param k: the supplied random nonce
    :param m: the message (is not hashed here, hash before passing)
    :param d: the private ecc key
    :param ecc_curve_affine: the ecc
    :return: signature, i.e. Point(r,s)
    """
    k = k % ecc_curve_affine.n
    Q = ecc_curve_affine.scalarMult(k, ecc_curve_affine.basePoint)
    r = Q.x
    if(r == 0):
        raise ValueError("ecdsa_k: r == 0!")
    kinv = ecc_curve_affine.inv_mod(k, ecc_curve_affine.n)
    s = (kinv *  ((m + ((r*d) % ecc_curve_affine.n)) % ecc_curve_affine.n)) % ecc_curve_affine.n
    if(s == 0):
        raise ValueError("ecdsa_k: s == 0!")
    return Point(r,s)



