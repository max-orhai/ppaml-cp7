# -*- coding: utf-8 -*-
"""
@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import numpy as np
import scipy.sparse as spa
import scipy.special
import pymc
import pymc.MCMC

from GaussianMRF import GaussianMRF


# log likelihood of observation using a log link function and Poisson distribution
# for the observation
def LogLinkPoissonObs(Coefficients, Predictor=None, Observation=None):
    ''' Log-likelihood of observation with Poisson noise and log link
    '''
    return (float(Coefficients[0]) + np.dot(Predictor.T, Observation[:,None])
        - np.sum(float(Coefficients[1])*np.exp(Predictor)))

def LinearLinkBetaObs(Coefficients, Predictor=None, Observation=None, Draw=False):
    ''' Log-likelihood of observation with Beta noise and linear link

    Coefficients[0] is the observation matrix (C in Cx) and is a
       Scipy sparse matrix
    Coefficients[1] is the precision parameter
    Cx is the mean of the Beta distribution.
    The Beta distribution is parameterized as in
    Ferrari and Cribari-Neto, 2004.
    '''

    mu = Coefficients[0].dot(Predictor)
    alpha = mu*Coefficients[1] # \mu * \phi
    beta = Coefficients[1]*(1-mu) # \phi * (1 - \mu)

    if Draw:
        # draw samples
        return scipy.stats.beta.rvs(alpha, beta)
    else:
        # compute log-likelihood
        return pymc.beta_like(Observation[:,None],alpha,beta)
    
# a dictionary used to define the functions that are available for random-effects term
RandomEffectsMethods = {"GaussianMRF": GaussianMRF}

# distributions that can be used for PyMC models
PyMC_Distributions = {"Gamma": pymc.Gamma,
                      "Normal": pymc.Normal}        

# link function and observation pair
LinkFuncObs = {("log", "Poisson"): LogLinkPoissonObs,
               ("linear", "Beta"): LinearLinkBetaObs}

# Define Generalized Linear Mixed-Effects Model Class
class GLMM(object):
    
    def __init__(self, RandEff_Param, FixedEff_Param, LinkObs_Param, gridParams,
                 isSparse = False, GridMask = np.array(np.NaN)):
        ''' Initialize a Generalized Linear Mixed Model (GLMM)
        
        Inputs:
            RandEff_Param: parameters used to define random-effects terms
            FixedEff_Param: parameters used to define fixed-effects terms, if any
            gridParams: parameters to define the underlying grid for computation
            isSparse: if True, the random-effects terms are constructed using sparse matrices
            GridMask: a mask to define the region of interest; data outside the
                region of interest is ignored in the estimation.
        '''
      
        self._RandEff_Param = RandEff_Param
        self._FixedEff_Param = FixedEff_Param
        self._LinkObs_Param = LinkObs_Param
        self._isSparse = isSparse
        self._gridParams = gridParams
        # dictionary variable to store estimation results
        self.Result = dict()
        # last sample (after thinning) of MCMC run
        self.lastMCMCsample = dict()
        
        # Initializing MRF based on how the random field is defined.
        # Currently, only the GMRF is defined. In the future, definitions of the
        # random field using covariance functions will be implemented.
        self.GMRF = list()
        for iDim in range(len(RandEff_Param)):
            self.GMRF.append(RandomEffectsMethods[RandEff_Param[iDim].Method](
                RandEff_Param[iDim], self._isSparse))
                    
            
    
    def Update(self, observations, UpdateParams):
        ''' Calculate posterior distributions of parameters and intensities
        
            Inputs:
                observations.data: an 1-D array of size prod(gridParams.N)
                    where each element contains the number of occurrences in the
                    corresponding cell. The 1-D array is arranged such that
                    The first dimension (gridParams.N[0]) counts the fastest,
                    followed by the second dimension, and so on.
                UpdateParams: a structure (object) that defines all of the parameters
                    that are needed in the computational schemes (MCMC or MAP)
        '''
        
        # Initial guess of GMRF values
        InitialGMRF = list()
        for ic in range(len(self.GMRF)):
            if spa.isspmatrix(self.GMRF[ic].bVec):
                InitialGMRF.append(self.GMRF[ic].bVec.todense())
            else:
                InitialGMRF.append(self.GMRF[ic].bVec)
                
        # define model for MCMC using PyMC
        
        # dictionary to store model variables
        ModelDict = {}

        
        #_________________________________________________________________________
        # Random variables (fixed-effects coefficients) related to fixed-effects terms

        # Prepare Coefficients for Fixed Effects for PyMC        
        # prior for fixed-effects coefficients fe_ceof_i
        fe_coef = list()
        if self._FixedEff_Param.FixedEffects.lower() == "estimated":
            # fixed-effects terms
            fe_coef.append(pymc.Normal(
                                'fe_coef_0',
                                mu=self._FixedEff_Param.Coeff_PriorMean[0],
                                tau=self._FixedEff_Param.Coeff_PriorPrec[0],
                                value=self._FixedEff_Param.Coeff_PriorMean[0]))            
            for i in range(1, self._FixedEff_Param.Coeff_PriorMean.size):
                fe_coef.append(pymc.Normal(
                    'fe_coef_%i' %i,
                    mu=self._FixedEff_Param.Coeff_PriorMean[i],
                    tau=self._FixedEff_Param.Coeff_PriorPrec[i],
                    value=self._FixedEff_Param.Coeff_PriorMean[i]))

        # Include fixed-effects coefficients in the model
        if len(fe_coef) > 0:
            ModelDict['FixedEffects'] = fe_coef
        
        
        
        #_________________________________________________________________________
        # Random variables related to hyper-parameters for the random-effects terms
        
        # Define multiplier for the precision of the random effects terms
        # If no hyperparameter is defined, the multiplier is 1 and the precision
        # is determined by the RandomField_Prec.
        gmrf_prec = list()
        for i in range(len(self.GMRF)):
            if len(self._RandEff_Param[i].HyperParam[0]) == 0:
                # no hyperparameters
                gmrf_prec.append(1.0)
            else:
                # use the probability distribution specified by users
                gmrf_prec.append(PyMC_Distributions[self._RandEff_Param[i].HyperParam[0]](
                    'gmrf_prec_%i' %i, **self._RandEff_Param[i].HyperParam[1]))
                 
        if len(gmrf_prec) > 0:
            # Include gmrf_prec in the model    
            ModelDict['gmrf_prec'] = gmrf_prec
            


        #_________________________________________________________________________
        # Random variables related to random-effects terms

        # Prepare all Random Effects Terms for PyMC
        RandomEffects = list()
        for i in range(len(self.GMRF)):
            @pymc.stochastic(dtype=float)
            def gmrf_spatial(value= InitialGMRF[i],
                             RandEff_Param = self._RandEff_Param[i],
                             PrecK = gmrf_prec[i],
                             PrecMat = self.GMRF[i].PrecMat):
                
                def logp(value, RandEff_Param, PrecK, PrecMat):
                    ''' log probability modulo a constant'''
                    # Note: dense array multiplying sparse matrix uses the
                    # matrix multiplication and returns a dense array
                    logp_prop = (((np.prod(np.array(RandEff_Param.N)-np.array(RandEff_Param.RankDef))/2)
                        * np.log(PrecK) - 0.5 * PrecK *
                        ((np.asmatrix(value.T) * PrecMat) * np.asmatrix(value))))                       
                                        
                    #type(logp_prop)
                    return logp_prop    # returns a numpy.matrix object
         
            # assign a unique name for each term
            gmrf_spatial.__name__ = 'gmrf_spatial_%i' %i
            
            # Combine all random effects terms in a list for the PyMC container class
            RandomEffects.append(gmrf_spatial)
            
        if len(self.GMRF) > 0:
            # Include random effects in the model
            ModelDict['RandomEffects'] = RandomEffects        
        


        #_________________________________________________________________________
        # Log odds at every node

        @pymc.deterministic
        def Predictor(FixedEffectsCoeff = fe_coef,
                      RandomEffects = RandomEffects,
                      FixedEffectsCovariates = self._FixedEff_Param.Covariates):

            # total number of nodes
            total_effects = np.zeros((np.prod(self._gridParams.N), 1))
            
            # Add random effects terms
            for ic in range(len(RandomEffects)):
                randeff = np.asarray(RandomEffects[ic])
                total_effects = total_effects + randeff
                    
            # Add fixed effects terms
            if len(self._FixedEff_Param.FixedEffects) > 0:
                total_effects += np.dot(FixedEffectsCovariates, np.array(FixedEffectsCoeff)[:,None])

            # inverse log-odds of total effects
            total_effects = scipy.special.expit(total_effects)
                    
            return total_effects

        # Include link function in the model
        ModelDict['Predictor'] = Predictor

                            
             
        #_________________________________________________________________________
        # Observations

        # Observed data
        @pymc.stochastic(dtype=float, observed=True)
        def Observation(value=observations, Predictor=Predictor):
            ''' Given predictor output (fixed and random effects), calculate 
                likelihood of the observation '''
    
            def logp(value, Predictor):
                ''' log likelihood '''
                return LinkFuncObs[self._LinkObs_Param.LinkFunc,
                                       self._LinkObs_Param.ObsDist](
                                           self._LinkObs_Param.LinkCoef,
                                           Predictor=Predictor,
                                           Observation=value)

        # Include observations in the model
        ModelDict['Observation'] = Observation
        
        #_________________________________________________________________________
        # Prepare model for PyMC
        
        #Model = pymc.Model({'RandomEffects': RandomEffects,
        #                    'gmrf_prec': gmrf_prec,
        #                    'FixedEffects': fe_coef,
        #                    'Predictor': Predictor,
        #                    'Observation': CountData})
        #Model = pymc.Model([RandomEffects, Predictor, Observation])
        Model = pymc.Model(ModelDict)
            

        #_________________________________________________________________________
        # PyMC Estimation (MCMC or MAP)
        
        if UpdateParams.Method == 'MCMC':    
            # MCMC sampling
            if UpdateParams.SessionDatabaseFile is None:
                # create a new database file to store the results
                PyMC_MCMC = pymc.MCMC([Model], db='pickle', dbname='samples.pkl')
                PyMC_MCMC.sample(UpdateParams.NumSample, burn=UpdateParams.NumBurnIn,
                                 thin=UpdateParams.Thinning)
                PyMC_MCMC.db.close()
            elif UpdateParams.SessionDatabaseFile.lower() == 'donot store':               
                # do not store the resutls (keep in RAM only)
                PyMC_MCMC = pymc.MCMC([Model])
                PyMC_MCMC.sample(UpdateParams.NumSample, burn=UpdateParams.NumBurnIn,
                                 thin=UpdateParams.Thinning)
            else:
                # Start from a existing database file that stores previous results
                # It also initializes all variables in MCMC so that the run is 
                # equivalent to continuation of the chains stored in the database.
                try:
                    db = pymc.database.pickle.load(UpdateParams.SessionDatabaseFile)
                    PyMC_MCMC = pymc.MCMC([Model], db=db)
                except:
                    PyMC_MCMC = pymc.MCMC([Model], db='pickle', dbname=UpdateParams.SessionDatabaseFile)
                PyMC_MCMC.sample(UpdateParams.NumSample, burn=UpdateParams.NumBurnIn,
                                 thin=UpdateParams.Thinning)
                PyMC_MCMC.db.close()
            
            
            # store MCMC samples
            #self.Result['FixEffCoef'] = PyMC_MCMC.trace('fe_coef_0')[:]
            #self.Result['FixEffCoef_1'] = PyMC_MCMC.trace('fe_coef_1')[:]
            
            # store MCMC samples (only random variables are saved)
            for key, val in ModelDict.items():
                # iterate through each term in the model
                # key contains model name (e.g. RandomEffects) and
                # val contains the corresponding random variables
                if isinstance(val, list):
                    # only random variables are saved in lists
                    for i in range(len(val)):
                        # iterate through each variable in the model term (e.g. RandomEffects)
                        # val[i].__name__ is the actual name for each variable
                        if isinstance(val[i], pymc.PyMCObjects.Stochastic):
                            self.Result[val[i].__name__] = PyMC_MCMC.trace(val[i].__name__)[:]

            
            # additional samples to save
            self.Result['Predictor'] = PyMC_MCMC.trace('Predictor')[:]
            

            #self.ModelDict = ModelDict            
        elif UpdateParams.Method == 'MAP':
            # maximum a posteriori
            PyMC_MAP = pymc.MAP([Model])            
            PyMC_MAP.fit()
            self.Result['MAP'] = PyMC_MAP
        else:
            raise ValueError("No such update method.")

        
    def DrawSamples(self):
        ''' Draw samples '''

        '''
        Draw a single sample from the random field and combine it with the
        deterministic terms. The combined effect defines the log-odd of
        realizing an event.
        '''
        
        # total number of nodes
        total_effects = np.zeros((np.prod(self._gridParams.N), 1))
        
        # Add random effects terms
        for ic in range(len(self.GMRF)):
            ## The first few diagonal elements of the precision matrix
            ## are added a small value to prevent singularity.
            #rowcol = [(0,0)] # (row, col)
            #epsilon = 0.000 # fraction of the current value to add
            ## find what the current value is
            #val = self.GMRF[ic].AcquirePrecMatElement(rowcol)
            ## assign the new value (1+epsilon) times the current value
            #self.GMRF[ic].AssignPrecMatElement(
            #    rowcol, [el*(1+epsilon) for el in val])
            ## draw a sample using the new precision matrix
            randeff = np.asarray(self.GMRF[ic].Draw_Sample(NumSmpl = 1))
            
            total_effects = total_effects + randeff

        # Add fixed effects terms
        if len(self._FixedEff_Param.FixedEffects) > 0:
            total_effects += np.dot(self._FixedEff_Param.Covariates,
                                    self._FixedEff_Param.Coeff_PriorMean[:,None])
        
        # inverse log-odds
        total_effects = scipy.special.expit(total_effects)

        # Observed data (Beta distribution)
        #Smpl = LinkFuncObs[self._LinkObs_Param.LinkFunc, self._LinkObs_Param.ObsDist](
        #    self._LinkObs_Param.LinkCoef, Predictor=total_effects, Draw=True)
        Smpl = total_effects
        
        return Smpl
