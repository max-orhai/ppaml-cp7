# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 09:49:05 2011

@author: Ssu-Hsin Yu (syu001@gmail.com)
"""

# Last modified: 09/22/2011 by:  Ssu-Hsin Yu

import numpy as np
from scipy.linalg import circulant
import scipy.sparse as spa 

# This module incorporates scipy sparse matrix operations and its functions
# returns sparse matrices when required.

def StrucMatR_FromDf(Dim, isSparse = False, Base = np.array(np.NaN)):
    '''
    Formulate structural matrix in one dimension
    
    Description:
        
    This function computes the structural matrix:
        R = Dx' Dx
        
    where Dx is the difference matrices for Neumann boundary
    conditions (BCs) for a Dim array.
    
    Input:
        
    Dim: an integer that defines the number of points along a line.
    isSparse: (default = False) if True, a sparse structural matrix is generated 
    Base: basis for both dimensions; default is [-1,1]
    
    Output:
        
    Struc_Mat: 2-D array, Dim by Dim, storing the corresponding structural matrix R
    '''
    
    # Difference matrix of the first dimension
    if np.all(np.isnan(Base)):
        RW1_Base = np.r_[-1, 1, np.zeros(Dim-2)]
        BaseSize = 2
    else:
        RW1_Base = np.r_[Base, np.zeros(Dim-Base.size)]
        BaseSize = Base.size
    RW1_DF = circulant(RW1_Base).T
    RW1_DF = RW1_DF[:Dim-(BaseSize-1),:] # if we want to remove the circulant effect
    
    # Calculate the structural matrix R = Dx' * Dx + Dy' * Dy
    if isSparse:
        Struc_Mat = spa.csr_matrix(np.dot(RW1_DF.T, RW1_DF))
    else:
        Struc_Mat = np.dot(RW1_DF.T, RW1_DF)
    
    return Struc_Mat


def StrucMatR_FromDfDf(Dim, isSparse = False, Base = np.array(np.NaN)):
    '''
    Formulate structural matrix from in regular lattice
    
    Description:
        
    This function computes the structural matrix:
        R = Dx' * Dx + Dy' * Dy
        
    where Dx and Dy are the difference matrices for Neumann boundary
    conditions (BCs) for the first and second dimensions of an Dim[0] x Dim[1]
    array respectively.
    
    Input:
        
    Dim: a two-element array that defines a grid. The first and second element
        determine the number of grid points along the first and second
        dimensions respectively. The grid points are numbered such that the
        first dimension counts fastest.
    isSparse: (default = False) if True, a sparse structural matrix is generated 
    Base: basis for both dimensions; default is [-1,1]
    
    Output:
        
    Struc_Mat: 2-D array, (Dim[0]*Dim[1]) by (Dim[0]*Dim[1]), storing the
        corresponding structural matrix R
    '''
    
    # Difference matrix of the first dimension
    if np.all(np.isnan(Base)):
        RW1_Base = np.r_[-1, 1, np.zeros(Dim[0]-2)]
        BaseSize = 2
    else:
        RW1_Base = np.r_[Base, np.zeros(Dim[0]-Base.size)]
        BaseSize = Base.size
    RW1_DF = circulant(RW1_Base).T
    RW1_DF = RW1_DF[:Dim[0]-(BaseSize-1),:] # if we want to remove the circulant effect
    
    # Difference matrix of the second dimension
    if np.all(np.isnan(Base)):
        RW2_Base = np.r_[-1, 1, np.zeros(Dim[1]-2)]
    else:
        RW2_Base = np.r_[Base, np.zeros(Dim[1]-Base.size)]
    RW2_DF = circulant(RW2_Base).T
    RW2_DF = RW2_DF[:Dim[1]-(BaseSize-1),:] # if we want to remove the circulant effect
    
    # Calculate the structural matrix R = Dx' * Dx + Dy' * Dy
    if isSparse:
        Struc_Mat = ( np.dot(spa.kron(spa.eye(Dim[1],Dim[1]), RW1_DF).T,
                             spa.kron(spa.eye(Dim[1],Dim[1]), RW1_DF)) +
                             np.dot(spa.kron(RW2_DF, spa.eye(Dim[0],Dim[0])).T,
                                    spa.kron(RW2_DF, spa.eye(Dim[0],Dim[0]))) )
    else:
        Struc_Mat = ( np.dot(np.kron(np.eye(Dim[1]), RW1_DF).T,
                             np.kron(np.eye(Dim[1]), RW1_DF)) +
                             np.dot(np.kron(RW2_DF, np.eye(Dim[0])).T,
                                    np.kron(RW2_DF, np.eye(Dim[0]))) )
    
    return Struc_Mat


def StrucMatR_FromRDf(Dim, RMat, isSparse = False, Base = np.array(np.NaN)):
    '''
    Extend existing structural matrix to an additional dimension in regular lattice
    
    Description:
        
    This function computes the structural matrix:
        R = (I kron R) + (Dz' * Dz)
        
    where Dz is the first-difference matrix for Neumann boundary
    conditions (BCs). When numbering the grid points, the new dimension counts
    the slowest.
    
    Inputs:
        
    Dim: integer that defines the number of grid points along the new dimension
    RMat: 2-D array that stores the structural matrix of the existing dimensions
    isSparse: (default = False) if True, a sparse structural matrix is generated
    Base: basis along the new dimension; default is [-1,1]
    
    Output:
        
    Struc_Mat: 2-D array, (RMap.shape[0]+Dim) by (RMap.shape[0]+Dim), that
        stores the new structural matrix
    '''
    
    if np.logical_xor(spa.issparse(RMat), isSparse):
        raise ValueError("RMat and isSparse have to be compatible")        
        
    # Difference matrix of the new dimension
    if np.all(np.isnan(Base)):
        RW2_Base = np.r_[-1, 1, np.zeros(Dim-2)]
        BaseSize = 2
    else:
        RW2_Base = np.r_[Base, np.zeros(Dim-Base.size)]
        BaseSize = Base.size
    RW2_DF = circulant(RW2_Base).T
    RW2_DF = RW2_DF[:Dim-(BaseSize-1),:] # if we want to remove the circulant effect

    # new structural matrix
    if isSparse:
        Struc_Mat = ( spa.kron(spa.eye(Dim,Dim), RMat) +
            np.dot(spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0])).T,
                   spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0]))) )
    else:
        Struc_Mat = ( np.kron(np.eye(Dim), RMat) +
            np.dot(np.kron(RW2_DF, np.eye(RMat.shape[0])).T,
                   np.kron(RW2_DF, np.eye(RMat.shape[0]))) )
    
    return Struc_Mat
        
def StrucMatR_FromDfDf_Inhomo(Dim, sx, sy, epsilon=0, isSparse = False, Base = np.array(np.NaN)):
    '''
    Formulate structural matrix in regular lattice.
    Instead of variance 1 for all difference between neighboring grid
    points (see StrucMatR_FromDfDf), this function allows any variancs
    assigned by a user.
    
    Description:

    This function computes the structural matrix:
        R = Dx' * diag( (1-epsilon)*(1-sx).^2 + epsilon ) * Dx + 
            Dy' * diag( (1-epsilon)*(1-sy).^2 + epsilon ) * Dy 
    
    where Dx and Dy are the first-difference matrices for Neumann boundary
    conditions (BCs) for the first and second dimensions of an Dim[0] x Dim[1]
    array respectively. (1-sx)^2 and (1-sy)^2 define the precision assigned by
    the user along the first and second dimensions respectively, with values
    ranging between zero and 1. The additional optional parameter, 'epsilon',
    which may range between zero and 1, effectively puts a lower bound on the
    weighting, which can improve the matrix condition number (for stability and
    reducing oversensitivity). If epsilon = 0, and all elements of sx and sy
    are 0, this function is equivalent to the homogeneous case
    "StrucMatR_FromDfDf."

    Input:
        
    Dim: a two-element array that defines a grid. The first and second element
        determine the number of grid points along the first and second
        dimensions respectively. The grid points are numbered such that the
        first dimension counts fastest.
    sx - a 1-D array of (Dim[0]-1) x Dim[1] elements such that (1-sx)^2 determines
        the precision of neighboring points along the first dimension. Hence,
        the first element determines the precision of the difference between the
        first and second elements on the grid, the second element between the
        second and third elements, and so on. The values
        of sx must be in range [0,1).            
    sy - a 1-D array of Dim[0] x (Dim[1]-1) elements such that (1-sy)^2 determines
        the precision of neighboring points along the second dimension. Hence,
        the first element determines the precision of the difference between the
        first and (Dim[0]+1) elements on the grid, the second element between
        the second and (Dim[0]+2) elements, and so on. The values
        of sy must be in range [0,1). 
    epsilon (optional) - optional stabilization/coupling parameter. Value
        must be in range [0,1]. Default is 0 (no stabilization).
        epsilon defines the minimum possible precision.
    isSparse: (default = False) if True, a sparse structural matrix is generated
    Base: basis for both dimensions; default is [-1,1]

        
    Output:
        
    Struc_Mat: 2-D array, (Dim[0]*Dim[1]) by (Dim[0]*Dim[1]), storing the
        corresponding structural matrix R
    '''

    # Make sure that the code works when sx and sy are either a 1-D array or
    # a 2-D array of 1 row or column.
    if sx.ndim == 2:
        sx = np.squeeze(sx)
    if sy.ndim == 2:
        sy = np.squeeze(sy)
    
    # Difference matrix of the first dimension
    if np.all(np.isnan(Base)):
        RW1_Base = np.r_[-1, 1, np.zeros(Dim[0]-2)]
        BaseSize = 2
    else:
        RW1_Base = np.r_[Base, np.zeros(Dim[0]-Base.size)]
        BaseSize = Base.size
    RW1_DF = circulant(RW1_Base).T
    RW1_DF = RW1_DF[:Dim[0]-(BaseSize-1),:] # if we want to remove the circulant effect
    
    # Difference matrix of the second dimension
    if np.all(np.isnan(Base)):
        RW2_Base = np.r_[-1, 1, np.zeros(Dim[1]-2)]
    else:
        RW2_Base = np.r_[Base, np.zeros(Dim[1]-Base.size)]
    RW2_DF = circulant(RW2_Base).T
    RW2_DF = RW2_DF[:Dim[1]-(BaseSize-1),:] # if we want to remove the circulant effect
    
    # Calculate the structural matrix R = Dx' * Dx + Dy' * Dy
    if isSparse:
        Struc_Mat = ( np.dot(np.dot(spa.kron(spa.eye(Dim[1],Dim[1]), RW1_DF).T,
                                    spa.dia_matrix(([(1-epsilon) * np.power(1-sx,2) + epsilon], 0),
                                                   shape = (len(sx),len(sx)))),
                            spa.kron(spa.eye(Dim[1],Dim[1]), RW1_DF)) +
                    np.dot(np.dot(spa.kron(RW2_DF, spa.eye(Dim[0],Dim[0])).T,
                                  spa.dia_matrix(([(1-epsilon) * np.power(1-sy,2) + epsilon], 0),
                                                 shape = (len(sy),len(sy)))),
                            spa.kron(RW2_DF, spa.eye(Dim[0],Dim[0]))) )
    else:
        Struc_Mat = ( np.dot(np.dot(np.kron(np.eye(Dim[1]), RW1_DF).T,
                                    np.diag((1-epsilon) * np.power(1-sx,2) + epsilon)),
                            np.kron(np.eye(Dim[1]), RW1_DF)) +
                    np.dot(np.dot(np.kron(RW2_DF, np.eye(Dim[0])).T,
                                  np.diag((1-epsilon) * np.power(1-sy,2) + epsilon)),
                            np.kron(RW2_DF, np.eye(Dim[0]))) )
    
    return Struc_Mat
    
    
def StrucMatR_FromRDf_Inhomo(Dim, RMat, sz, epsilon=0, isSparse = False, Base = np.array(np.NaN)):
    '''
    Extend existing structural matrix to an additional dimension in regular lattice.
    Instead of variance 1 for all difference
    between neighboring grid points along the new dimension (see
    StrucMatR_FromRDf), this function allows any variancs assigned by a user.
    
    Description:
        
    This function computes the structural matrix:
        R = (I kron R) + (Dz' * diag( (1-epsilon)*(1-sz).^2 + epsilon ) * Dz)
        
    where Dz is the first-difference matrix for Neumann boundary
    conditions (BCs). When numbering the grid points, the new dimension counts
    the slowest.
    
    Inputs:
        
    Dim: integer that defines the number of grid points along the new dimension
    RMat: 2-D array that stores the structural matrix of the existing dimensions
    sz - a 1-D array of 'RMat.shape[0]*(Dim-1)' elements such that (1-sz)^2 determines
        the precision of neighboring points along the new dimension. Hence,
        the first element determines the precision of the difference between the
        first and RMat.shape[0]+1 elements on the grid, the second element
        between the second and RMat.shape[0]+2 elements, and so on.
        The values of sz must be in range [0,1).       
    epsilon (optional) - optional stabilization/coupling parameter. Value
        must be in range [0,1]. Default is 0 (no stabilization).
        epsilon defines the minimum possible precision.
    isSparse: (default = False) if True, a sparse structural matrix is generated
    Base: basis along the new dimension; default is [-1,1]
    
    Output:
        
    Struc_Mat: 2-D array, (RMap.shape[0]+Dim) by (RMap.shape[0]+Dim), that
        stores the new structural matrix
    '''

    if np.logical_xor(spa.issparse(RMat), isSparse):
        raise ValueError("RMat and isSparse have to be compatible")
        
    # Make sure that the code works when sx and sy are either a 1-D array or
    # a 2-D array of 1 row or column.
    if sz.ndim == 2:
        sz = np.squeeze(sz)

    # Difference matrix of the new dimension
    if np.all(np.isnan(Base)):
        RW2_Base = np.r_[-1, 1, np.zeros(Dim-2)]
        BaseSize = 2
    else:
        RW2_Base = np.r_[Base, np.zeros(Dim-Base.size)]
        BaseSize = Base.size
    RW2_DF = circulant(RW2_Base).T
    RW2_DF = RW2_DF[:Dim-(BaseSize-1),:] # if we want to remove the circulant effect

    # new structural matrix
    if isSparse:
        Struc_Mat = ( spa.kron(spa.eye(Dim,Dim), RMat) +
            np.dot(np.dot(spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0])).T,
                          spa.dia_matrix(([(1-epsilon) * np.power(1-sz,2) + epsilon], 0),
                                         shape = (len(sz),len(sz)))),
                spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0]))) )
    else:
        Struc_Mat = ( np.kron(np.eye(Dim), RMat) +
            np.dot(np.dot(np.kron(RW2_DF, np.eye(RMat.shape[0])).T,
                          np.diag((1-epsilon) * np.power(1-sz,2) + epsilon)),
                np.kron(RW2_DF, np.eye(RMat.shape[0]))) )
    
    return Struc_Mat


def StrucMatPeriodic_FromDf(Dim, Period, isSparse = False):
    '''
    Formulate structural matrix in one dimension that is invariant under
    periodic fluctuation
    
    Description:
        
    This function computes the structural matrix:
        R = Dx' Dx
        
    where each element of Dx is the sum of Dim number of consecutive variables
    along a line. The effect is that the structure matrix R is invariant to the
    addition of any vector of the form
    (a1, a2, ..., a_(m-1), -a1-a2-...-a_(m-1), a1, a2, ...)
    
    Input:
        
    Dim: an integer that defines the number of points along a line.
    isSparse: (default = False) if True, a sparse structural matrix is generated 
    Period: period of the fluctuation
    
    Output:
        
    Struc_Mat: 2-D array, Dim by Dim, storing the corresponding structural matrix R
    '''
    
    # Difference matrix of the first dimension
    RW1_Base = np.r_[np.ones(Period), np.zeros(Dim-Period)]
    RW1_DF = circulant(RW1_Base).T
    RW1_DF = RW1_DF[:Dim-(Period-1),:] # if we want to remove the circulant effect
    
    # Calculate the structural matrix R = Dx' * Dx + Dy' * Dy
    if isSparse:
        Struc_Mat = spa.csr_matrix(np.dot(RW1_DF.T, RW1_DF))
    else:
        Struc_Mat = np.dot(RW1_DF.T, RW1_DF)
    
    return Struc_Mat

def StrucMatPeriodic_FromRDf(Dim, Period, RMat, isSparse = False):
    '''
    Formulate structural matrix in one dimension that is invariant under
    periodic fluctuation
    
    Description:
        
    This function computes the structural matrix:
        R = (I kron R) + (Dx' * Dx)
        
    where each element of Dx is the sum of Dim number of consecutive variables
    along a line. The effect is that the structure matrix R is invariant to the
    addition of any vector of the form
    (a1, a2, ..., a_(m-1), -a1-a2-...-a_(m-1), a1, a2, ...)
    
    Inputs:
        
    Dim: integer that defines the number of grid points along the new dimension
    Period: period of the fluctuation
    RMat: 2-D array that stores the structural matrix of the existing dimensions
    isSparse: (default = False) if True, a sparse structural matrix is generated
    Base: basis along the new dimension; default is [-1,1]
    
    Output:
        
    Struc_Mat: 2-D array, (RMap.shape[0]+Dim) by (RMap.shape[0]+Dim), that
        stores the new structural matrix
    '''
    
    if np.logical_xor(spa.issparse(RMat), isSparse):
        raise ValueError("RMat and isSparse have to be compatible")        

    # Difference matrix of the first dimension
    RW2_Base = np.r_[np.ones(Period), np.zeros(Dim-Period)]
    RW2_DF = circulant(RW2_Base).T
    RW2_DF = RW2_DF[:Dim-(Period-1),:] # if we want to remove the circulant effect
        
    # new structural matrix
    if isSparse:
        Struc_Mat = ( spa.kron(spa.eye(Dim,Dim), RMat) +
            np.dot(spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0])).T,
                   spa.kron(RW2_DF, spa.eye(RMat.shape[0],RMat.shape[0]))) )
    else:
        Struc_Mat = ( np.kron(np.eye(Dim), RMat) +
            np.dot(np.kron(RW2_DF, np.eye(RMat.shape[0])).T,
                   np.kron(RW2_DF, np.eye(RMat.shape[0]))) )
    
    return Struc_Mat
