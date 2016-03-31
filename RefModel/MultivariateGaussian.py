# -*- coding: utf-8 -*-
"""
MultivariateGaussian class
Define a multivariate Gaussian distribution with user specified mean or b
vectors and covariance or precision matrices. After initialization, mean, b,
covariance and precision can be speficied directly, and the related variables
will be changed accordingly.
According to the defined distribution, users can draw random samples or update
mean (and b) and covariance (and precision) conditional on measurements. 

Created on Tue Aug 30 23:13:25 2011

In [43]: a = MultiG.MultivariateGaussian(meanVec = np.zeros((2,1)),
                                         CovMat = 2*np.eye(2))
In [44]: a.meanVec
Out[44]: 
array([[ 0.],
       [ 0.]])
       
In [45]: a.CovMat
Out[45]: 
array([[ 2.,  0.],
       [ 0.,  2.]])
       
In [46]: a.bVec
Out[46]: 
array([[ 0.],
       [ 0.]])
       
In [47]: a.PrecMat
Out[47]: 
array([[ 0.5,  0. ],
       [ 0. ,  0.5]])
       
In [48]: a.bVec = np.array([[1],[1]])

In [49]: a.bVec
Out[49]: 
array([[1],
       [1]])

In [50]: a.meanVec
Out[50]: 
array([[ 2.],
       [ 2.]])
       
b = spa.coo_matrix(np.array([[1.],[1.]]))
b = b.tocsr()
b[0,0] = 0
b[1,0] = 0
c = spa.coo_matrix(([1,2], ([0,1],[0,1])))


@author: Ssu-Hsin Yu (syu001@gmail.com)
"""


import numpy as np
import scipy.sparse as spa
# import scipy.sparse.linalg
import cvxopt.cholmod as cholmod
from cvxopt import spmatrix as cvxspa
from cvxopt import matrix as cvxmatrix


class MultivariateGaussian(object):
    
    def __init__(self, meanVec = np.array(np.NaN), CovMat = np.array(np.NaN),
        bVec = np.array(np.NaN), PrecMat = np.array(np.NaN), isSparse = False):
        '''
        Initialization with defined mean, b, covariance, or precision.
        User can specified any combination of the above 4 variables with the
        following constraints:
            1. Either meanVec or bVec but not both has to be specified.
            2. Either CovMat or PrecMat but not both has to be specified.
        
        meanVec: 2D column array denoting mean vector
        bVec: 2D column array denoting b vector (canonical form)
        CovMat: 2D square array denoting covariance matrix
        PrecMat: 2D square array denoting precision matrix
        isSparse: if True, all inputs are sparse matrix
        
        All of the input matrices have to be in the same format. They can be
        either numpy arrays or scipy sparse matrices. If they are numpy arrays,
        isSparse should be False (default). Otherwise, isSparse should be True.
        Also, once isSparse is specified, all subsequent operations of the same
        object have to follow the same format.
        '''

        # determine which inputs are defined and make sure that isSparse
        # is compatible with the matrix format.
        self._DefinedInput= dict({"Mean": False, "b": False, "Cov": False, "Prec": False})
        if spa.issparse(meanVec):
            self._DefinedInput["Mean"] = True
            if not isSparse: raise ValueError("MeanVec is not dense")
        else:
            if np.all(~np.isnan(meanVec)):
                self._DefinedInput["Mean"] = True
                if isSparse: raise ValueError("MeanVec is not sparse")
        if spa.issparse(bVec):
            self._DefinedInput["b"] = True
            if not isSparse: raise ValueError("bVec is not dense")
        else:
            if np.all(~np.isnan(bVec)):
                self._DefinedInput["b"] = True
                if isSparse: raise ValueError("bVec is not sparse")
        if spa.issparse(CovMat):
            self._DefinedInput["Cov"] = True
            if not isSparse: raise ValueError("CovMat is not dense")
        else:
            if np.all(~np.isnan(CovMat)):
                self._DefinedInput["Cov"] = True
                if isSparse: raise ValueError("CovMat is not sparse")
        if spa.issparse(PrecMat):
            self._DefinedInput["Prec"] = True
            if not isSparse: raise ValueError("PrecMat is not dense")
        else:
            if np.all(~np.isnan(PrecMat)):
                self._DefinedInput["Prec"] = True
                if isSparse: raise ValueError("PrecMat is not sparse")
        
        # Verify if the multivariate Gaussian is specified properly
        if not(self._DefinedInput["Mean"]) and not(self._DefinedInput["b"]):
            raise ValueError("Either mean or b needs to be specified")
        if not(self._DefinedInput["Cov"]) and not(self._DefinedInput["Prec"]):
            raise ValueError("Either covariance or precision matrix needs to be specified")
        if self._DefinedInput["Mean"] and self._DefinedInput["b"]:
            raise ValueError("Mean and b cannot be both specified")
        if self._DefinedInput["Cov"] and self._DefinedInput["Prec"]:
            raise ValueError("Covariance or precision matrices cannot be both specified")            
                    
        # initialization 
        # Eeither mean or b vector is specified. The other is NaN.
        # Similarly, either covariance or precision matrix is specified.
        self._meanVec = meanVec.copy()
        self._CovMat = CovMat.copy()
        self._bVec = bVec.copy()
        self._PrecMat = PrecMat.copy()
        
        # whether the matrices are sparse or dense
        self._isSparse = isSparse
                       
    @property
    def meanVec(self):
        ''' Return mean vector '''
        
        if self._DefinedInput["Mean"]: # mean vector already exists
            return self._meanVec.copy()
        else:
            if not self._isSparse:
                # dense matrix                
                if self._DefinedInput["Cov"]:
                    # calculate mean from b and covariance matrix
                    return np.dot(self._CovMat, self._bVec)
                else:
                    # calculate mean from b and precision matrix 
                    Lmat = np.linalg.cholesky(self._PrecMat)
                    wVec = np.linalg.solve(Lmat, self._bVec)
                    return np.linalg.solve(Lmat.T, wVec)
            else:
                # sparse matrix
                if self._DefinedInput["Cov"]:
                    # calculate mean from b and covariance matrix
                    # scipy.spase '*' means matrix multiplicaton
                    return self._CovMat * self._bVec
                else:
                    # calculate mean from b and precision matrix
                
                    # Convert to CVXOPT sparse matrix format from scipy.sparse
                    cvxPrecMat = cvxspa(self._PrecMat.data, self._PrecMat.nonzero()[0],
                                        self._PrecMat.nonzero()[1], self._PrecMat.shape)
                    # b at the right-hand side of the linear equation
                    rhs = cvxmatrix(self._bVec.todense())
                    # linear solver (Cholesky) to invert precision matrix
                    cholmod.linsolve(cvxPrecMat, rhs)
                    # return the result in np.array format instead of CVXOPT matrix
                    return np.array(rhs)
                
    @meanVec.setter
    def meanVec(self, meanVec):
        ''' Assign mean vector '''
        
        if np.logical_xor(self._isSparse, spa.issparse(meanVec)):
            raise ValueError("isSparse has to be compatible with the assigned value.")
        self._meanVec = meanVec.copy()
        self._DefinedInput["Mean"] = True
        self._bVec = np.NaN # either mean or b can be specified
        self._DefinedInput["b"] = False
        
    @property
    def bVec(self):
        ''' Return b vector '''
        
        if self._DefinedInput["b"]: # b vector already exists
            return self._bVec.copy()
        else:
            if not self._isSparse:
                # dense matrix
                if self._DefinedInput["Prec"]:
                    # calculate b from mean and precision matrix
                    return np.dot(self._PrecMat, self._meanVec)
                else:
                    # calculate b from mean and covariance matrix
                    Lmat = np.linalg.cholesky(self.CovMat)
                    wVec = np.linalg.solve(Lmat, self._meanVec)
                    return np.linalg.solve(Lmat.T, wVec)
            else:
                # sparse matrix
                if self._DefinedInput["Prec"]:
                    # calculate mean from b and precision matrix
                    # scipy.spase '*' means matrix multiplicaton
                    return self._PrecMat * self._meanVec
                else:
                    # calculate b from mean and covariance matrix
                
                    # Convert to CVXOPT sparse matrix format from scipy.sparse
                    cvxCovMat = cvxspa(self._CovMat.data, self._CovMat.nonzero()[0],
                                       self._CovMat.nonzero()[1], self._CovMat.shape)
                    # mean at the right-hand side of the linear equation
                    rhs = cvxmatrix(self._meanVec.todense())
                    # linear solver (Cholesky) to invert precision matrix
                    cholmod.linsolve(cvxCovMat, rhs)
                    # return the result in np.array format instead of CVXOPT matrix
                    return np.array(rhs)

    @bVec.setter
    def bVec(self, bVec):
        ''' Assign b vector '''
        
        if np.logical_xor(self._isSparse, spa.issparse(bVec)):
            raise ValueError("isSparse has to be compatible with the assigned value.")
        self._bVec = bVec.copy()
        self._DefinedInput["b"] = True
        self._meanVec = np.NaN # either mean or b can be specified
        self._DefinedInput["Mean"] = False

    @property
    def CovMat(self):
        ''' Return covariance matrix '''
        
        if self._DefinedInput["Cov"]: # covariance matrix already exists
            return self._CovMat.copy()
        else:
            if not self._isSparse:
                # dense matrix
                Lmat = np.linalg.cholesky(self._PrecMat)
                wVec = np.linalg.solve(Lmat, np.eye(self._PrecMat.shape[0]))
                return np.linalg.solve(Lmat.T, wVec)
            else:
                # sparse matrix
                
                # Convert to CVXOPT sparse matrix format from scipy.sparse
                cvxPrecMat = cvxspa(self._PrecMat.data, self._PrecMat.nonzero()[0],
                                    self._PrecMat.nonzero()[1], self._PrecMat.shape)
                # identity matrix at the right-hand side of the linear equation
                rhs = cvxmatrix(np.eye(self._PrecMat.shape[0]))
                # linear solver (Cholesky) to invert precision matrix
                cholmod.linsolve(cvxPrecMat, rhs)
                # return the result in np.array format instead of CVXOPT matrix
                return np.array(rhs)

    @CovMat.setter
    def CovMat(self, CovMat):
        ''' Assign covariance matrix '''
        
        if np.logical_xor(self._isSparse, spa.issparse(CovMat)):
            raise ValueError("isSparse has to be compatible with the assigned value.")
        self._CovMat = CovMat.copy()
        self._DefinedInput["Cov"] = True
        self._PrecMat = np.NaN # either covariance or precision matrix can be specified
        self._DefinedInput["Prec"] = False

    @property
    def PrecMat(self):
        ''' Return precision matrix '''
        
        if self._DefinedInput["Prec"]: # covariance matrix already exists
            return self._PrecMat.copy()
        else:
            if not self._isSparse:
                # dense matrix
                Lmat = np.linalg.cholesky(self._CovMat)
                wVec = np.linalg.solve(Lmat, np.eye(self._CovMat.shape[0]))
                return np.linalg.solve(Lmat.T, wVec)
            else:
                # sparse matrix
                
                # Convert to CVXOPT sparse matrix format from scipy.sparse
                cvxPrecMat = cvxspa(self._CovMat.data, self._CovMat.nonzero()[0],
                                    self._CovMat.nonzero()[1], self._CovMat.shape)
                # identity matrix at the right-hand side of the linear equation
                rhs = cvxmatrix(np.eye(self._CovMat.shape[0]))
                # linear solver (Cholesky) to invert precision matrix
                cholmod.linsolve(cvxPrecMat, rhs)
                # return the result in np.array format instead of CVXOPT matrix
                return np.array(rhs)

    @PrecMat.setter
    def PrecMat(self, PrecMat):
        ''' Assign precision '''

        if np.logical_xor(self._isSparse, spa.issparse(PrecMat)):
            raise ValueError("isSparse has to be compatible with the assigned value.")        
        self._PrecMat = PrecMat.copy()
        self._DefinedInput["Prec"] = True
        self._CovMat = np.NaN # either covariance or precision matrix can be specified
        self._DefinedInput["Cov"] = False

    def AssignPrecMatElement(self, rowcol, val):
        '''
        Assign values to specific elements in the precision matrix.
        The precision matrix has to be already defined.
        rowcol: a list of 2 tuples containing the indices whose corresponding
        elements are to be assigned. For example, [(0,0)].
        val: the values to be assigned to the elements
        '''
        if not self._DefinedInput["Prec"]: # precision matrix not immediately available
            raise ValueError("To assign individual elements, precision matrix needs to be defined first")
        for cnt, idx in zip(range(len(rowcol)), rowcol):
            self._PrecMat[idx[0],idx[1]] = val[cnt]

    def AcquirePrecMatElement(self, rowcol):
        '''
        Given the row and column indices, return the corresponding
        elements in the precision matrix.
        rowcol: a list of 2 tuples containing the indices to return
        element values. For example, [(0,0)].
        '''
        if not self._DefinedInput["Prec"]: # precision matrix not immediately available
            raise ValueError("To assign individual elements, precision matrix needs to be defined first")
        val = []
        for idx in rowcol:
            val.extend([self._PrecMat[idx[0],idx[1]]])
        return val

    def Draw_Sample(self, NumSmpl = 100):
        '''
        Draw random samples from a multivariate Gaussian distribution
        NumSmpl: the total number of samples to be drawn     
        
        The function returns a Numpy 2-D array that has as many columns as the
        number of samples.
        '''     
        
        # Choose a sampling method depending on how GMRF is defined
        if self._DefinedInput["b"] and self._DefinedInput["Prec"]:
            # canonical form b vector and precision matrix
            RandomSmpl = self.MultivarNormalSample_Canonical(self._bVec, self._PrecMat,
                                                             self._isSparse, NumSmpl)
        elif self._DefinedInput["Mean"] and self._DefinedInput["Prec"]:
            # mean and precision matrix form
            RandomSmpl = self.MultivarNormalSample_MeanPrec(self._meanVec, self._PrecMat,
                                                            self._isSparse, NumSmpl)
        elif self._DefinedInput["Mean"] and self._DefinedInput["Cov"]:
            # mean and covariance matrix form
            RandomSmpl = self.MultivarNormalSample_MeanCov(self._meanVec, self._CovMat,
                                                           self._isSparse, NumSmpl)
        else:
            raise ValueError("Mean (or b) and covariance (precision) matrix need to be specified")
        
        return RandomSmpl

    
    def MultivarNormalSample_Canonical(self, bVec, PrecMat, isSparse, NumSmpl=100):
        '''
        Drawing samples from a multivariate normal distribution expressed in
        the canonical form b vector and precision matrix
        '''
        
        if not isSparse:
            # dense matrix
            Lmat = np.linalg.cholesky(PrecMat)
            wVec = np.linalg.solve(Lmat, bVec)
            meanVec = np.linalg.solve(Lmat.T, wVec)
            IndNrmlSmpl = np.random.standard_normal(size = (wVec.size, NumSmpl))
            vVec = np.linalg.solve(Lmat.T, IndNrmlSmpl)
            return meanVec + vVec
        else:
            # sparse matrix
            
            # Convert to CVXOPT sparse matrix format from scipy.sparse
            cvxPrecMat = cvxspa(PrecMat.data, PrecMat.nonzero()[0], PrecMat.nonzero()[1], PrecMat.shape)
            # symbolic analysis of a sparse real symmetric matrix. The output
            # C object contains the information of Cholesky factorization that
            # can be used by other CHOLMOD functions.
            FMat = cholmod.symbolic(cvxPrecMat)
            # numeric factorization
            cholmod.numeric(cvxPrecMat, FMat)
            # L x = b (sys=4)
            # The solution is saved in rhs_bVec
            rhs_bVec = cvxmatrix(bVec.todense())
            cholmod.solve(FMat, rhs_bVec, sys=4)
            # L^T x = b where b is now the solution in the last statement
            # The solution of the following statement would give us the mean
            cholmod.solve(FMat, rhs_bVec, sys=5)
            # draw samples from independent normal distribution
            IndNrmlSmpl = np.random.standard_normal(size = (PrecMat.shape[0], NumSmpl))
            IndNrmlSmpl = cvxmatrix(IndNrmlSmpl)
            # Convert to normal distribution samples to Gaussian distribution
            # of desired precision matrix and save the result in IndNrmlSmpl
            cholmod.solve(FMat, IndNrmlSmpl, sys=5)
            # return the result in np.array format instead of CVXOPT matrix
            return np.array(rhs_bVec) + np.array(IndNrmlSmpl)

    
    def MultivarNormalSample_MeanCov(self, meanVec, CovMat, isSparse, NumSmpl=100):
        '''
        Drawing samples from a multivariate normal distribution expressed in
        mean and covariance matrix
        '''
        
        # Convert everything to dense matrices (ndarray)
        # Can't find a way to extract L from CVXOPT.cholmod
        # and covariance matrix is usually dense anyway.
        if isSparse:
            Lmat = np.linalg.cholesky(np.array(CovMat.todense()))
        else:
            Lmat = np.linalg.cholesky(CovMat)
            
        # draw samples from independent normal distribution
        IndNrmlSmpl = np.random.standard_normal(size = (meanVec.size, NumSmpl))
        # random samples of zero mean Gaussian distribution with CovMat
        vVec = np.dot(Lmat, IndNrmlSmpl)
        
        if isSparse:
            return np.array(meanVec.todense()) + vVec
        else:
            return meanVec + vVec            
            
            
    def MultivarNormalSample_MeanPrec(self, meanVec, PrecMat, isSparse, NumSmpl=100):
        '''
        Drawing samples from a multivariate normal distribution expressed in
        mean and precision matrix
        '''
        
        if not isSparse:
            # dense matrix
            Lmat = np.linalg.cholesky(PrecMat)
            IndNrmlSmpl = np.random.standard_normal(size = (meanVec.size, NumSmpl))
            vVec = np.linalg.solve(Lmat.T, IndNrmlSmpl)
            return meanVec + vVec
        else:
            # sparse matrix
            
            # Convert to CVXOPT sparse matrix format from scipy.sparse format
            cvxPrecMat = cvxspa(PrecMat.data, PrecMat.nonzero()[0], PrecMat.nonzero()[1], PrecMat.shape)
            # symbolic analysis of a sparse real symmetric matrix. The output
            # C object contains the information of Cholesky factorization that
            # can be used by other CHOLMOD functions.
            FMat = cholmod.symbolic(cvxPrecMat)
            # numeric factorization
            cholmod.numeric(cvxPrecMat, FMat)
            # draw samples from normal distribution
            IndNrmlSmpl = np.random.standard_normal(size = (meanVec.size, NumSmpl))
            IndNrmlSmpl = cvxmatrix(IndNrmlSmpl)
            # Convert to normal distribution samples to Gaussian distribution
            # of desired precision matrix and save the result in IndNrmlSmpl
            # Solve L^T x = b (sys=5)
            cholmod.solve(FMat, IndNrmlSmpl, sys=5)
            return meanVec + np.array(IndNrmlSmpl)
            

    def PosteriorNormal(self, CMmntMat, MmntVec, MmntVarVec):
        '''
        Calculate the posterior b vector and precision matrix conditional on 
        measurements. The relationship has the following form 
            Y = C X + n
        where n is an independent measurement noise, Y is the measurement, and
        X is the Gaussian distributed random variable currently defined.
        
        CMmntMat: C matrix; MxN array
        MmntVec: measurements; 1xM or Mx1 array
        MmntVarVec: variance of the measurements; 1xM or Mx1 array
        
        Note: If isSparse is True, all of the inputs have to be sparse matrices.
        Similarly, if isSparse is False, all of the inputs have to be dense matrices.
        '''
        
        # Make sure that matrices are compatible
        if np.any(np.logical_xor(
            [spa.issparse(CMmntMat), spa.issparse(MmntVec), spa.issparse(MmntVarVec)],
            [self._isSparse, self._isSparse, self._isSparse])):
                raise ValueError("Input matrices should be compatible with isSparse")

    
        # Convert measurement vector and corresponding variances to row vectors
        if MmntVec.shape[0] != 1: MmntVec = MmntVec.T
        if MmntVarVec.shape[0] != 1: MmntVarVec = MmntVarVec.T
        
        # The following code is divided into dense and sparse matrix operations
        # since the multiplication '*' has different meanings.
        # Sparse matrix operations follow matrix conventions where '*' means
        # matrix multiplications.
        if not self._isSparse:
            # dense matrix
            # For dense matrix operations, the numpy broadcasting rules are
            # utilized in the computation.
            # Posterior precision matrix
            # Qn = Q + C^T PrecM C
            self.PrecMat = ( self.PrecMat +
                np.dot(CMmntMat.T * np.reciprocal(MmntVarVec), CMmntMat) )
    
            # Posterior b vector in canonical form (m = Q^-1 b)
            # bn = b + C^T PrecM y
            self.bVec = ( self.bVec +
                np.dot(CMmntMat.T, (np.reciprocal(MmntVarVec) *  MmntVec).T) )
        else:
            # sparse matrix
            # For sparse matrix operations, the matrix operations are utilized.
            # Posterior precision matrix
            self.PrecMat = ( self.PrecMat + CMmntMat.T *
                spa.dia_matrix((MmntVarVec.todense(), np.array([0])),
                               shape=(MmntVarVec.size,MmntVarVec.size)) *  CMmntMat )    
            # Posterior b vector in canonical form (m = Q^-1 b)
            self.bVec = ( self.bVec + CMmntMat.T *
                spa.dia_matrix((MmntVarVec.todense(), np.array([0])),
                               shape=(MmntVarVec.size,MmntVarVec.size)) * MmntVec.T )
        
    def MmntStat(self, CMmntMat):
        '''
        Acquire statistics of random variables that are linear transformation
        of the Gaussian random variables:
            Z = CX
        where X denotes the Gaussian random vector, and Z is the random
        vector of interest.
        
        Input:
            CMmntMat: C matrix; MxN array
            
        Output:
            locMean: mean vector of the random vector of interest (M x 1 array)
        '''
        
        # Make sure that matrices are compatible
        if np.logical_xor(self._isSparse, spa.issparse(CMmntMat)):
            raise ValueError("Input matrices should be compatible with isSparse")
            
        if not self._isSparse:
            locMean = np.dot(CMmntMat, self.meanVec)
            #locVar = np.dot(np.dot(CMmntMat, self.CovMat), CMmntMat.T)
        else:
            locMean = CMmntMat * self.meanVec
        
        #return locMean, locVar
        return locMean
        
