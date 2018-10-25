# RingCT2: a dumb implementation of a sublinear ring signature scheme
#
# Use this code only for prototyping
# -- putting this code into production would be dumb
# -- assuming this code is secure would also be dumb

from dumb25519 import *
import MultiSig

def elgamal_encrypt(X,r):
    return [H*r + X, G*r]

def elgamal_commit(x,r):
    return [H*r + G*x, G*r]
    
    
# Decompose an integer with a given base
# INPUT
#   base: type int
#   n: integer to decompose; type int
#   exponent: maximum length of result; type int
# OUTPUT
#   int list
def decompose(base,n,exponent):
    if not isinstance(base,int) or not isinstance(n,int) or not isinstance(exponent,int):
        raise TypeError
    if base < 2 or n < 0 or exponent < 1:
        raise ValueError

    result = []
    for i in range(exponent-1,-1,-1):
        base_pow = base**i
        result.append(n/base_pow)
        n -= base_pow*result[-1]
    return list(reversed(result))

# Kronecker delta function
# INPUT
#   x,y: any type supporting equality testing
# OUTPUT
#   Scalar: 1 if the inputs are the same, 0 otherwise
def delta(x,y):
    try:
        if x == y:
            return Scalar(1)
        return Scalar(0)
    except:
        raise TypeError

# Scalar matrix commitment
# INPUT
#   m: matrix; list of Scalar lists
#   r: mask; type Scalar
# OUTPUT
#   Point
def matrix_commit(m,r):
    if not isinstance(r,Scalar):
        raise TypeError

    data = [[G,r]] # multiexp data
    for i in range(len(m)):
        for j in range(len(m[0])):
            if not isinstance(m[i][j],Scalar):
                raise TypeError
            data.append([hash_to_point('pyruff '+str(i)+' '+str(j)),m[i][j]])
    return multiexp(data)



def keyGen(params):
    # We assume params is a dictionary of key-value pairs where each key
    # is a short string describing the parameter and each value is the
    # corresponding parameter
    numSecretKeys = params['numKeys']
    sk = []
    for i in range(numKeys):
        sk.append(random_scalar())
    
    ki = G*sk[1]
    pk = elgamal_encrypt(ki, sk[0])
    
    return (sk, ki, pk)
    
def sub(kis, PK, cos, co, m, f):
    L = len(PK) # number of inputs
    N = len(PK[0]) # ring size
    PKZ = []
    eff = []
    for j in range(L):
        PKZ.append([kis[j],Z])
        eff.append(hash_to_scalar(str(kis[j]) + str(f) + str(j)))
    C = []
    for i in range(N):
        data0 = [[cos[i], Scalar(1)]] # multiexp data (first component)
        data1 = [[cos, Scalar(1)]] # multiexp data (second component)

        for j in range(L):
            data0.append([PK[j][i][0], eff[j]])
            data0.append([PKZ[j][0], -eff[j]])
            data1.append([PK[j][i][1], eff[j]])
            data1.append([PKZ[j][1], -eff[j]])

        C.append([multiexp(data0),multiexp(data1)])

    return C
    
def spend(sks, kis, t, PK, cos, m):
    L = len(PK) # number of inputs
    N = len(PK[0]) # ring size
    assert L == len(sks)
    assert L == len(kis)
    assert N == len(cos)
    
    ownt = H*t
    canSign = None
    signerIdx = None
    for i in range(N):
        if cos[i] == ownt:
            canSign = True
            signerIdx = i
    assert canSign
    
    co = G*t
    f = [kis, PK, cos, co, m]
    C = sub(kis, PK, cos, co, m, f)
    r = t
    for j in range(L):
        r += sks[j][0]*hash_to_scalar(str(kis[j]) + str(f) + str(j))
        
    signing_randomness = [[random_scalar() for i in range(N)] for j in range(L)]
    sigma1 = bootleProve(C, (signerIdx, r), signing_randomness)
    sigma2 = sign([sks[j][1] for j in range(L)], (sigma1, f))
    return (co, sigma1, sigma2)
    
def spendVer(kis, PK, cos, m, (co, sigma1, sigma2)):
    L = len(PK) # number of inputs
    N = len(PK[0]) # ring size
    
    
    if L == len(kis) and N == len(co):
        f = [kis, PK, cos, co, m]
        C = sub(kis, PK, cos, co, m, f)
        if not verify(kis, (sigma2, f)):
            b = 0
        else:
            b = bootleValid(sigma1, C)
    else:
        b = 0
    return b
    
def bootleProve(cos, (ell, r), signing_randomness, base, exponent):
    size = base**exponent
    assert size == len(cos)
    
    ell_seq = decompose(base, ell, exponent)
    d = []
    for j in range(exponent):
        d.append([])
        for i in range(base):
            d[j].append(delta(ell_seq[j],i))
    
    rb = signing_randomness[0]
    rho = signing_randomness[1:exponent+1]
    ra = signing_randomness[exponent+1]
    rc = signing_randomness[epxonent+2]
    rd = signing_randomness[exponent+3]
    
    amatrix = []
    idx = exponent+4
    for i in range(exponent-1):
        a.append([Scalar(0)])
        for j in range(base): 
            a[-1].append(signing_randomness[idx])
            a[-1][0] -= signing_randomness[idx]
            idx += 1
            
    cmatrix = [[amatrix[j][i]*(Scalar(1)-Scalar(2)*d[j][i]) for j in range(base)] for i in range(exponent)]
    dmatrix = [[-amatrix[j][i]*amatrix[j][i] for j in range(base)] for i in range(exponent)]
    A = matrix_commit(amatrix, ra)
    B = matrix_commit(d,rB)
    C = matrix_commit(cmatrix, rc)
    D = matrix_commit(dmatrix, rd)
    coefs = coefficients(amatrix, ell, ell_seq)
    pointSequence = []
    for k in range(exponent):
        data0 = [[H,rho[k]]]
        data1 = [[G,rho[k]]]
        for i in range(size):
            data0.append([cos[i][0],coefs[i][k]])
            data1.append([cos[i][1],coefs[i][k]])
        pointSequence.append([multiexp(data0),multiexp(data1)])
        
    challenge = str(cos) + str(A) + str(B) + str(C) + str(D) + str(pointSequence)
    x = hash_to_scalar(challenge)
    
    fullf = []
    for j in range(base):
        f.append([])
        for i in range(exponent):
            fullf[j].append(d[j][i]*x + amatrix[j][i])
    f = [[f[j][i] for j in range(base)] for i in range(1,exponent)]
    za = r*x + ra
    zc = rc*x + rd
    z = r*x**exponent
    for i in range(exponent):
        z -= rho[i]*x**i
        
    outProof = [A, B, C, D, pointSequence, f, za, zc, z]
        
    return [cos, outProof]
    
def bootleVerify(cos, outProof):
    A = outProof[0]
    B = outProof[1]
    C = outProof[2]
    D = outProof[3]
    pointSequence = outProof[4]
    f = outProof[5]
    za = outProof[6]
    zc = outProof[7]
    z = outProof[8]
    
    result = 0
    pointCheck = isinstance(A, Point) and isinstance(B, Point) and isinstance(C, Point) and isinstance(D, Point)
    for p in pointSequence:
        pointCheck = pointCheck and isinstance(p, Point)
    if pointCheck:
        scalarCheck = isinstance(f, Scalar) and isinstance(za, Scalar) and isinstance(zc, Scalar) and isinstance(z, Scalar)    
        if scalarCheck:
            challenge = str(cos) + str(A) + str(B) + str(C) + str(D) + str(pointSequence)
            x = hash_to_scalar(challenge)
            new_eff = []
            for j in range(base):
                new_eff.append([x])
                for i in range(exponent-1):
                    new_eff[j].append(f[j][i])
                    new_eff[j][0] -= f[j][i]
            effPrime = [[new_eff[j][i]*(x-new_eff[j][i]) for j in range(base)] for i in range(exponent)]
            bxaCheck = (B*x + A == matrix_commit(new_eff, za))
            cxdCheck = (C*x + D == matrix_commit(effPrime, zc))
            if bxaCheck and cxdCheck:
                g = []
                g.append(f[0][0])
                for j in range(1,exponent):
                    g[0] *= f[j][0]

                data0 = [[cos[0][0],g[0]]]
                data1 = [[cos[0][1],g[0]]]
                for i in range(1,base**exponent):
                    i_seq = decompose(base,i,exponent)
                    g.append(f[0][i_seq[0]])
                    for j in range(1,exponent):
                        g[i] *= f[j][i_seq[j]]
                    data0.append([CO[i][0],g[i]])
                    data1.append([CO[i][1],g[i]])

                for k in range(exponent):
                    data0.append([pointSequence[k][0],-x**k])
                    data1.append([pointSequence[k][1],-x**k])

                if [multiexp(data0),multiexp(data1)] == elgamal_encrypt(Z,z):
                    result = 1
                    
    return result
    
