# -*- coding: utf-8 -*-
"""
@author: Ssu-Hsin Yu
"""

import numpy as np
import scipy.sparse as spa

import StrucMat
import MultivariateGaussian as MultiG


class GMRF(object):
    ''' An empty class object to store anything similar to the structure format
    '''
    pass

# Using closure to define zero matrices that work for both sparse and dense matrices
def make_zero_matrix(isSparse):
    def zero_matrix(shape):
        if isSparse:
            return spa.csr_matrix(shape)
        else:
            return np.zeros(shape)
    return zero_matrix

# Define Gaussian Markov Random Field
def GaussianMRF(paramClass, isSparse=False, isNoSample=False):
    ''' Construct a GMRF class

    Inputs:
      paramClass: parameters for defining the GMRF
      isSparse: if True, GMRF is constructed using sparse matrices
      isNoSample: if True, the precision and b vector definition is used to
        define the GMRF, and it doesn't have the ability to draw samples or
        convert to other GMRF definition (e.g. mean, covariance)
    Output:
      GMRF object where b and precision matrix are its members.
        If isNoSample is false, then it can be used to draw samples or
        compute mean and covariance matrix.
    '''
    
    # zero matrix function whose format (sparse or dense) is defined by users
    zero_matrix = make_zero_matrix(isSparse)
    
    # Formulate Structural Matrix for GMRF 
    if paramClass.StrucMat[0].lower() == "strucm":
        # The structural matrix is directly assigned
        StrucM = paramClass.StrucMatParam[0]
    elif paramClass.StrucMat[0].lower() == "basis":
        # The structural matrix is generated using user specified "basis"
        StrucM = (paramClass.RandomFieldWeight[0]*
            StrucMat.StrucMatR_FromDf(paramClass.N[0],
                                      isSparse = isSparse,
                                      Base = paramClass.StrucMatParam[0]))
    elif paramClass.StrucMat[0].lower() == "periodic":
        # The structural matrix is invariant to periodic fluctuations
        StrucM = (paramClass.RandomFieldWeight[0]*
            StrucMat.StrucMatPeriodic_FromDf(paramClass.N[0],
                                             paramClass.StrucMatParam[0],
                                             isSparse = isSparse))

    # Expand the structural matrix to additional dimensions
    for iDim in range(1,len(paramClass.StrucMat)):
        if paramClass.StrucMat[iDim].lower() == "strucm":
            # The structural matrix is directly assigned
            raise ValueError("Direct assignment can only be used for the first element")
        elif paramClass.StrucMat[iDim].lower() == "basis":
            StrucM = (  
                StrucMat.StrucMatR_FromRDf(
                    paramClass.N[iDim], StrucM,
                    isSparse = isSparse,
                    Base = paramClass.RandomFieldWeight[iDim]**0.5 * paramClass.StrucMatParam[iDim]))
        elif paramClass.StrucMat[iDim].lower() == "periodic":
            StrucM = ( paramClass.RandomFieldWeight[iDim] *
                StrucMat.StrucMatPeriodic_FromRDf(
                    paramClass.N[iDim],
                    paramClass.StrucMatParam[iDim],
                    StrucM/paramClass.RandomFieldWeight[iDim],
                    isSparse = isSparse))
    
    # normalize the structural matrix so that each row adds up to 1
    #StrucM = StrucM / StrucM.sum(axis=1)
    for row in range(StrucM.shape[0]):
        nzidx = StrucM[row,:].nonzero()
        StrucM[row,nzidx[1]] = StrucM[row,nzidx[1]]/StrucM[row,row]

    if isNoSample:
        # return a GMRF object that has b and prec. matrix as its only members
        GMRF.bVec = zero_matrix((StrucM.shape[0], 1))
        GMRF.PrecMat = paramClass.RandomField_Prec * StrucM
        return GMRF
    else:
        # return a multivariate Gaussian distribution object (GMRF)                
        return MultiG.MultivariateGaussian(
            bVec = zero_matrix((StrucM.shape[0], 1)),
            PrecMat = paramClass.RandomField_Prec * StrucM,
            isSparse = isSparse)
