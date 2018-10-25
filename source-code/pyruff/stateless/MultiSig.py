# MultiSig: sign a message with a vector of keys
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

from dumb25519 import *

# Sign a message with a list of secret keys
# INPUT
#   m: message to sign; any type representable by a string
#   x: list of secret keys; type Scalar
# OUTPUT
#   Multisignature
def sign(m, x):
    if len(x) == 0:
        raise ValueError('Signature must use at least one secret key!')
    for i in x:
        if not isinstance(i,Scalar):
            raise TypeError('Secret key must be of type Scalar!')
    try:
        i = str(m)
    except:
        raise TypeError('Cannot convert message!')

    n = len(x)
    X = []
    for i in range(n):
        X.append(G*x[i])
    strX = ''.join([str(i) for i in sorted(X,key = lambda j: str(j))])

    r = random_scalar() # Only one person is signing, so only one random number is necessary
    R = G*r
    c = hash_to_scalar(strX + str(R) + str(m))
    s = Scalar(0)
    s += r
    for i in range(n):
		s += c*x[i]
    return (R, s)

# Verify a message with a list of public keys
# INPUT
#   m: message to verify; any type representable by a string
#   X: list of public keys; type Point
#   sig: signature; type Multisignature
# OUTPUT
#   b: a bit, 0 indicating failure and 1 indicating valid signature
def verify(m, X, (R, s)):
    if len(X) == 0:
        raise ValueError('Signature must use at least one public key!')
    for i in X:
        if not isinstance(i,Point):
            raise TypeError('Public key must be of type Point!')
    try:
        i = str(m)
    except:
        raise TypeError('Cannot convert message!')
    if not isinstance(R, Point):
        raise TypeError('Signature element R must be of type Point!')
	if not isinstance(s, Scalar):
		raise TypeError('Signature element s must be of type Scalar!')

    n = len(X)
    strX = ''.join([str(i) for i in sorted(X,key = lambda j: str(j))])

    c = hash_to_scalar(strX + str(R) + str(m))
    S = G*s
	
    data = [[R, Scalar(1)]]
    for i in range(n):
        data.append([X[i],c])
	
    b = None
    # Check if R + c*X == S
    if not multiexp(data) == S:
        b = 0
    else:
        b = 1
    return b
