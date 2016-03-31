"""
Define covariates for fixed-effets terms

@author: Ssu-Hsin Yu
"""

from datetime import datetime, date, timedelta
import numpy as np

## Define covariates and arrange them in the same order as the
#  spatio-temporal grid (adjacency matrix)
#
# @param CntData: dictionary storing vaccination, tweets and other related
#  information about a county
# @param CountyName: dictionary defining the order in which each county
#  appear in the adjacency matrix:
#  {(county, state): (order, FIPS)}
# @param earliest: (None) if defined, the earliest date of the covariates; Otherwise,
#  using the earliest date in CntData 
# @param latest: (None) if defined, the latest data of the covarites; Otherwise,
#  using the latest date in CntData 
# @param[out] Covariates: numpy array [number of grid points, number of covariates]
def DefineCovariates(CntData, CountyName, earliest=None, latest=None):
    
    # number of covariates at each location/node
    NUMCOV = 3
        
    # find ealiest and latest dates
    fips = "01001" # Autauga, AL
    dates = []
    dates.extend([datetime.strptime(d, '%m/%d/%Y')
                  for d in CntData[fips]['Vaccination percentage %'].keys()])
    if not earliest: # no earliest date specified
        earliest = min(dates)
    if not latest: # no latest date specified
        latest = max(dates)

    # initialize covariates in the given order    
    num_counties = len(CountyName.keys())
    num_weeks = int((latest - earliest).days / 7) + 1
    Covariates = np.zeros((num_counties*num_weeks, NUMCOV))
    # Other variables of interest
    NUMVAR = 6
    OtherVar = np.zeros((num_counties*num_weeks, NUMVAR))

    # formulate covariates in the given order
    w_end = earliest
    wk = 0
    while w_end <= latest:
        for name in CountyName.keys():
            fips = CountyName[name][1] # county FIPS code
                
            # normalized number of tweets
            collegeFrac = CntData[fips]['Bachelor\'s degree or higher, percent of persons age 25+, 2009-2013']/100.
            collegeplus = 0.3 # frac of adults with a college degree or more using Twitter from Pew
            collegeminus = 0.2 # frac of adults (0.16+0.24)/2 with less than a college degree using Twitter from Pew
            tweetPop = (CntData[fips]['Population, 2014 estimate'] *
                (collegeFrac*collegeplus + (1.-collegeFrac)*collegeminus))
            nrmlCnst = 100000. # per 100000 pop.
            covTweet = nrmlCnst*(CntData[fips]['No. of Tweets'][w_end.strftime('%m/%d/%Y')])/tweetPop
            
            # numbe of unvaccinated Medicare recipients as a factor of (approx.) total population
            covVacc = ((1.0-CntData[fips]['Vaccination percentage %'][w_end.strftime('%m/%d/%Y')]/100.) *
                (CntData[fips]['Persons 65 years and over, percent, 2013']/100.)) # between 0 and 1
            
            # normalized population density
            nrmlCnstDen = 100.
            covPopden = (CntData[fips]['Population per square mile, 2010'] / nrmlCnstDen)
            
            Covariates[num_counties*wk+CountyName[name][0],] = (
                covTweet, covVacc, covPopden)
            
            '''
            Covariates[num_counties*wk+CountyName[name][0],] = (
                CntData[fips]['No. of Tweets'][w_end.strftime('%m/%d/%Y')],
                CntData[fips]['Population per square mile, 2010']/10.)
            '''
            
            # Other variables of interest
            OtherVar[num_counties*wk+CountyName[name][0],] = (
                CntData[fips]['Population, 2014 estimate'],
                CntData[fips]['High school graduate or higher, percent of persons age 25+, 2009-2013'],
                CntData[fips]['Bachelor\'s degree or higher, percent of persons age 25+, 2009-2013'],
                CntData[fips]['Persons 65 years and over, percent, 2013'],
                CntData[fips]['Persons under 18 years, percent, 2013'],
                CntData[fips]['Per capita money income in past 12 months (2013 dollars), 2009-2013'])
        wk = wk + 1 # counter
        w_end = w_end + timedelta(days=7) # date

    

    # transform the range of covariates to -\infty to \infty
    epsilon_2 = 1.
    epsilon_3 = 0.001
    epsilon_4 = 0.01
    Covariates = np.array((np.log(Covariates[:,0]+epsilon_2),
        np.log(np.divide(Covariates[:,1]+epsilon_3,1-Covariates[:,1]+epsilon_3)),
        np.log(Covariates[:,2]+epsilon_4))).T
    #Covariates = np.array((np.log(np.divide(Covariates[:,0]+epsilon_2,OtherVar[:,0])),
    #    np.log(Covariates[:,1]+epsilon_3))).T
    #Covariates = np.array((Covariates[:,0],)).T
    #Covariates = np.array((np.divide(Covariates[:,0],1-Covariates[:,0]),np.divide(Covariates[:,1],1-Covariates[:,1]))).T
        
    return Covariates


#import sys
#sys.path.append('/home/syu/Work/ppaml/software/data/GIS')
#import GIS_Utilities
#root = "/home/syu/Work/ppaml/data/GIS"
#filename = "county_adjacency_lower48.txt"
#(AdjMatrix, CountyName, CountyAdjDict)= GIS_Utilities.ConstructCountyAdjMatrix(filename,root)
#
