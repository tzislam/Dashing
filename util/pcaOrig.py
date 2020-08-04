import scipy
import numpy as np
import math as mp
import warnings

def pcaOrig(X, no_dims):
    # Ported from MATLAB to Python by Albert Furlong, 5/07/2019
    # INPUT: 
    #       X: A higher dimension array data field. 
    #       no_dims: An integer representation of the
    #                number of dimensions in X.
    # OUTPUT: A reduced dimensionality matrix containing valuable data.
    #  

    if (no_dims is None):
        no_dims = 2
    #Normalize the matrix
    
    X = X-np.mean(X, axis = 0)
    
    #Compute covariance matrix,
    if (np.shape(X)[1] < np.shape(X)[0]):
        C = np.cov(X, rowvar= False)
    else:
        C = np.dot(1 / np.shape(X)[0], np.dot(X, X.T)  )
    #Remove all NaN or inf elements
    
    C[C == np.inf] = 0
    C[C == np.nan] = 0
    
    #lam: Eigval, #M = Eigvec
    lam, M = np.linalg.eig(C)
    
    lam = np.sort(lam)[::-1]
    idx = np.argsort(lam)[::-1]
    
    M = M[idx]
    lam = lam[idx]
   
    if (no_dims > np.shape(X)[1]):
        no_dims = np.shape(X)[1]
        warnings.warn('Target dimensionality reduced to %d.' % no_dims)
    if (no_dims < 1):
        #TODO: Needs testing
        no_dims = np.where(np.cumsum(lam / np.sum(lam)) >= no_dims)[0]
    
    M = M[:,idx[0:no_dims]]
    lam = lam[0:no_dims]
    
    if (not (np.shape(X)[1] < np.shape(X)[0])):
        #TODO: Needs testing
        #FIXME: Must be adapted from MATLAB code
        M = np.dot(X.T , M);
        M = np.multiply(M, np.transpose(np.divide(1, np.sqrt( np.multiply(np.shape(X)[0],lam)))))
    
    mappedX = np.dot(X, M)
    mappingM = M
    #Match behaviour of MATLAB.
    return mappedX, mappingM
    
