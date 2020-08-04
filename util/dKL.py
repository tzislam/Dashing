import numpy as np
import math as m

def dKL(pmu, psigma, qmu, qsigma):
    # Ported from MATLAB to Python by Albert Furlong, 4/29/2019
    # INPUT:
    #       P and Q, passed in as a variance and average.
    # OUTPUT:
    #   delta, the KL divergence between p and q. 
    
    mu0 = np.asarray(pmu)
    mu1 = np.asarray(qmu)
    k = np.size(mu0)
    sigma0 = np.asarray(psigma)
    sigma1 = np.asarray(qsigma)
    tmp = sigma0/sigma1
    #Modified Kullback Leibler since all input is scalar.
    dKL = 0.5 *(tmp + ((mu1-mu0)/((mu1-mu0) * sigma1))-k-m.log(tmp))

    return dKL
