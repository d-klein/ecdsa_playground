ECDSA Playground
################

# About

A collection of ECDSA implementations, typically found on ressource-constrained devices such as smartcards.
These implementations are intended to

- get intermediate values when conducting side channel analysis
- generate simulation traces to test attack implementations

but are not ready for production use! In particular, they are not side channel resistant, although some
feature impelmentation details that are intended to study side channel resistance.

# Implementations

- `01_plain_double_add`: textbook ECC double & add implemented with affine coordinates. Plain ECDSA.
  
- `02_projective_double_add`: textbook double & add implemented with projective coordinates. Scalar blinding
  with user-provided random. Scalar is not blinded.
    
- `03_projective_comb`: double & add always implementation with projective coordinates. 
  Scalar blinding with user-provided random. Scalar multiplication with comb-method
  and window-size 2. Scalar is not blinded. For further 
  reference cf. Lomne and Roche: "A side journey into Open Titan"
  
- `04_shamir_trick` : double & add using projective coordinates and Shamir's trick. Shamir's trick
  is here not used for signature verification, but rather for scalar multiplication by splitting
  kP = k_0P + k_1 \lambda P, where k_0 and k_1 are the lower resp. upper half of bits of k. \lambda P
  is precomputed. For further reference cf. Rondepierre: Revisiting Atomic Patterns for Scalar
  Multiplications on Elliptic Curves and Solinas: Low-Weight Binary Representations for Pairs of Integers
  - variant a): the scalar is represented as a binary number
  - variant b): the scalar is represented in ternary form with minimal hamming weight (non adjacent form)
  - variant c): the scalar is represented in ternary form, but without zeros. This only works is lsb==1.
  
# Paper References
  
