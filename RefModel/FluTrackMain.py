"""
Main script to run the hierarchical spatio-temporal model for CP7

@author: Ssu-Hsin Yu (syu@ssci.com)
"""

import sys
import os.path as osp
import simplejson as json
from collections import OrderedDict
import numpy as np
import scipy.sparse as spa
from datetime import datetime

import SaveSmpl
import GIS_Utilities
import FluSpread
# To read observations and construct measurement matrix
import ConstructMmentMatrix as CM
# To generate covariates based on vaccination & tweet data in JSON
import DefineCovariates as DC

class Parameters(object):
    ''' An empty class object to store anything similar to the structure format
    '''
    pass


def main():
    param_file = sys.argv[1]
    input_dir = sys.argv[2]
    output_dir = sys.argv[3]
    log_dir = sys.argv[4]

    #_________________________________________________________________________
    ## Supporting data files that are used in the processing
    #   including adjacency map, tweet counts, etc.
    #

    # file that stores adjacent counties of each county in US (lower 48)
    adj_fn = osp.join(input_dir, 'county_adjacency_lower48.txt')

    # files that stores covariates in JSON format
    VaccTweets_fn = (osp.join(input_dir, "Flu_Vacc_Tweet_TRAIN.json"),
                     osp.join(input_dir, "Flu_Vacc_Tweet_TEST.json"))

    # file that stores the mapping from regions/states/districs to counties
    map_fn = osp.join(input_dir, 'Region2CountyMap.json')


    #_________________________________________________________________________
    ## ILI data files for training and testing
    #
    #

    data_fn = osp.join(input_dir, 'Flu_ILI.csv')

    # specify whether to use sparse matrix formulation
    isSparse = True


    #_________________________________________________________________________
    ## JSON file that stores the results
    #
    #

    result_fn = osp.join(output_dir, "result.json")


    #_________________________________________________________________________
    ## Specify the earlies and latest dates for processing
    #
    # If the dates are empty strings, then their values are defined by
    #  the earlies or latest dates of the covariates
    earliest=datetime.strptime('09/28/2013','%m/%d/%Y')
    latest=datetime.strptime('05/23/2015','%m/%d/%Y')

    #_________________________________________________________________________
    ## Specify the states of interest for processing in 2-letter state postal code
    # If empty or None, then all states are of interest.

    STATES = None


    #_________________________________________________________________________
    ## Load all of the data and prepare them for processing
    #
    #

    # construct county adjacency matrix
    (AdjMatrix, CountyName, CountyAdjDict)=GIS_Utilities.ConstructCountyAdjMatrix(adj_fn,STATES=STATES)

    # construct spatial structural matrix from the adjacency matrix
    Dw = np.squeeze(np.asarray(AdjMatrix.sum(axis=1)))
    StrucMat = spa.spdiags(Dw,0,AdjMatrix.shape[0],AdjMatrix.shape[0]) - AdjMatrix

    if not isSparse:
        StrucMat = StrucMat.todense()

    # read the covariates
    with open(VaccTweets_fn[0], 'rb') as fobj:
        # the first file
        CntData = json.load(fobj, object_pairs_hook=OrderedDict)
    for fn in VaccTweets_fn[1:]:
        # subsequent files
        with open(fn, 'rb') as fobj:
            tmpCntData = json.load(fobj, object_pairs_hook=OrderedDict)
        for key in tmpCntData.keys():
            if key in CntData:
                for wk in tmpCntData[key]['No. of Tweets']:
                    CntData[key]['No. of Tweets'][wk] = tmpCntData[key]['No. of Tweets'][wk]
                if 'Vaccination percentage %' in tmpCntData[key]:
                    # no vaccination data available on the state level and 3 counties
                    for wk in tmpCntData[key]['Vaccination percentage %']:
                        CntData[key]['Vaccination percentage %'][wk] = tmpCntData[key]['Vaccination percentage %'][wk]


    # determine the earliest and latest dates if they haven't been
    # specified earlier
    if (not earliest) or (not latest): # if either of them is empty
        # find ealiest and latest dates
        fips = "01001" # use Autauga, AL as an example
        dates = []
        dates.extend([datetime.strptime(d, '%m/%d/%Y')
                      for d in CntData[fips]['Vaccination percentage %'].keys()])
        if not earliest: # no earliest date specified
            earliest = min(dates)
        if not latest: # no latest date specified
            latest = max(dates)
    # total number of weeks
    num_weeks = int((latest - earliest).days / 7) + 1

    # number of cells in temporal dimension
    temporalGrid = num_weeks

    # number of cells in spatial dimension
    spatialGrid = len(CountyName)




    #_________________________________________________________________________
    # Define random effects terms for GLMM
    #
    # Each element in the list defines a random-effect term.
    RandEff_Param = list()


    # The following definition of Random Effects is an example of spatio-temporal
    # model where the spatial relationship is explicitly defined by a structural
    # matrix and the temporal relationship is defined by a basis.
    RandEff_Param.append(Parameters())
    RandEff_Param[0].Method = "GaussianMRF" # random effects method GMRF
    RandEff_Param[0].StrucMat = ("StrucM", "Basis") # define the methods to form the structural matrix for each dimension
    RandEff_Param[0].StrucMatParam = (StrucMat, np.array([-1,1])) # For each dimension, defines the basis
    RandEff_Param[0].RankDef = (1, 0) # the total rank deficiency of each element of StrucMat
    RandEff_Param[0].RandomFieldWeight = np.array([1.0, 20.0]) # For each dimension, defines the weighting
    RandEff_Param[0].N = (spatialGrid, temporalGrid) # For each dimension, the number of random variables (grid points)
    #RandEff_Param[0].Dim = (0, 1) # The corresponding grid dimension

    # The overall precision to be mutiplied to the normalized structure matrix
    RandEff_Param[0].RandomField_Prec = 5.

    # Define hyperparameters for the multiplicative coefficient of the precision matrix
    # The mean value of variance is GammaMean time RandomField_Prec
    GammaMean = 2.0 #5.0 # mean of Gamma distribution
    GammaVar = 2.0 # variance of Gamma distribution
    beta = GammaMean / GammaVar
    alpha = GammaMean * beta
    # (PDF, {arguments for PDF})
    # If PDF is an empty string (lenght 0), then no hyperparameters are specified
    # and the precision is explicitly determined by RandomField_Prec
    RandEff_Param[0].HyperParam = ("Gamma", {"alpha": alpha, "beta": beta})
    #RandEff_Param[0].HyperParam = ("", {})



    #_________________________________________________________________________
    # Define fixed effects for GLMM
    #

    FixedEff_Param = Parameters()

    # Define Covariates of Fixed Effects
    #-----------------------------------
    #
    # If there is no fixed effects, simply set
    # FixedEff_Param.FixedEffects = ""
    # then anything else for FixedEff_Param will be ignored

    # Covariates for the fixed effects. The covariates are defined for each node.

    # read covariates related to county vaccination and tweets
    Covariates = DC.DefineCovariates(CntData, CountyName, earliest, latest)
    # Covariates
    FixedEff_Param.Covariates = Covariates


    # Define Coefficients of Fixed Effects
    #-------------------------------------
    #

    # "Estimated": to be estimate from data
    # If it is empty, then no fixed effects are present
    FixedEff_Param.FixedEffects = "Estimated"
    #FixedEff_Param.FixedEffects = ""

    # Prior distributions of the fixed-effects coefficients to be estimated
    # The priors have Gaussian distributions with each element corresponding to a
    # fixed-effect coefficient term.

    FixedEff_Param.Coeff_PriorMean = np.array([0., 0., 0.])
    FixedEff_Param.Coeff_PriorPrec = np.array([0.2, 0.2, 0.2])




    #_________________________________________________________________________
    # Define link function and observation distribution for GLMM
    #

    # Specify the region (as defined in the header of csv truth file) not to be
    # considered. This is typically used to avoid conflicting/overlapping regions.
    #Region2Avoid = ['HHS Region 4', 'NC']
    Region2Avoid = []

    # read observed data and C matrix (as in Cx)
    (C_obs, ObsData) = CM.ConstructMmentMatrix(data_fn, map_fn, CountyName,
                                               (earliest, latest), CountyInfo=CntData,
                                                region2avoid=Region2Avoid)

    '''
    # set the observation to be identity matrix to save data of all counties
    # observation C matrix (as in Cx)
    num_row = Covariates.shape[0]
    if isSparse:
        C_obs = spa.eye(num_row)
    else:
        C_obs = np.eye(num_row)
    '''

    # Beta distribution coefficients
    #beta_prec = 5000 # the larger the value, the smaller the variance
    beta_prec = 1000 # the larger the value, the smaller the variance

    LinkObs_Param = Parameters()
    LinkObs_Param.LinkFunc = "linear"
    LinkObs_Param.ObsDist = "Beta"
    LinkObs_Param.LinkCoef= (C_obs, beta_prec)


    #_________________________________________________________________________
    # Define parameters related to estimation of LGCP coefficients

    UpdateParams = Parameters()
    UpdateParams.Method = 'MCMC' # method for PyMC estimation (either 'MCMC' or 'MAP')
    #UpdateParams.Method = 'MAP'
    UpdateParams.NumSample = 10 # total number of epochs (including burn-in) in MCMC
    UpdateParams.NumBurnIn = 0 # number of epochs during burn-in
    UpdateParams.Thinning = 1 # thining the number of epochs to be stored

    # The database file where the previous MCMC runs are stored.
    # None: start from scratch, and store the results in 'samples.pkl'
    # 'xxxx.pkl': a pickle file that stores previous results from which to continue MCMC sampling
    # 'donot store': don't store any results in a file
    #UpdateParams.SessionDatabaseFile = 'flu_est.pkl'
    #UpdateParams.SessionDatabaseFile = None
    UpdateParams.SessionDatabaseFile = 'donot store'


    #_________________________________________________________________________
    ## Initialization (creating a generative model object)

    gridParams = Parameters()
    gridParams.N = Covariates.shape[0] # total number of nodes

    print 'Initialization'
    model = FluSpread.GLMM(RandEff_Param, FixedEff_Param, LinkObs_Param,
                       gridParams, isSparse = isSparse)

    #_________________________________________________________________________
    ## Update (MCMC sampling of posterior)

    print 'Update'
    #a.Update(ObsData, UpdateParams)
    # add a small constant to avoid 0% ILI, which is outside the support of Beta dist.
    model.Update(ObsData+0.001, UpdateParams)


    #_________________________________________________________________________
    ## Save results from the posterior


    start_date = earliest
    end_date = latest
    # multiplied by 100 to be percentage
    SaveSmpl.SaveSmpl(100.*np.mean(model.Result['Predictor'][:,:,0],axis=0), result_fn, CountyName, start_date, end_date)
    return

if __name__ == "__main__":
    main()
