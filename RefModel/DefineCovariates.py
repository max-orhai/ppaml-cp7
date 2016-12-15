"""
Define covariates for fixed-effets terms

@author: Ssu-Hsin Yu
"""

from datetime import datetime, timedelta
import numpy as np
import simplejson as json
import scipy.signal

SmoothMethod = {'median': scipy.signal.medfilt}
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
# @param CovName: a list of names for the covariates
# @param map_fn: JSON file that stores the counties that are in each
#  region, state or district listed in the data file data_fn. Only used
#  to find what counties are in a state when summing tweets
# @param smooth: (None) a dictionary whose keys are the names of the covariates to
#  be filtered, and whose values are tuples of the form (method, filter parameters).
#  The filter parameters are defined as a dictionary which can be packed as arguments
#  of the filtering method "method."
# @param[out] Covariates: numpy array [number of grid points, number of covariates]
def DefineCovariates(CntData, CountyName, earliest=None, latest=None, CovName=None,
                     map_fn=None, smooth=None):
    
    # number of covariates at each location/node
    NUMCOV = len(CovName)

    # small numbers to avoid numerical problems for log()    
    epsilon_2 = 1.
    epsilon_3 = 0.001
    epsilon_4 = 0.01
    
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

    # read the mapping from region to counties
    # mapping: {region name: {FIPS: county name}}
    if map_fn:
        with open(map_fn, 'rb') as fobj:
            mapping = json.load(fobj)


    # formulate covariates in the given order
    w_end = earliest
    wk = 0
    while w_end <= latest:
        for name in CountyName.keys():
            fips = CountyName[name][1] # county FIPS code
            tmp_cov = []
            for cov_name in CovName:
                if cov_name == 'No. of Tweets':
                    # normalized number of tweets
                    collegeFrac = CntData[fips]['Bachelor\'s degree or higher, percent of persons age 25+, 2009-2013']/100.
                    collegeplus = 0.3 # frac of adults with a college degree or more using Twitter from Pew
                    collegeminus = 0.2 # frac of adults (0.16+0.24)/2 with less than a college degree using Twitter from Pew
                    tweetPop = (CntData[fips]['Population, 2014 estimate'] *
                        (collegeFrac*collegeplus + (1.-collegeFrac)*collegeminus))
                    nrmlCnst = 100000. # per 100000 pop.
                    covTweet = nrmlCnst*(CntData[fips]['No. of Tweets'][w_end.strftime('%m/%d/%Y')])/tweetPop
                    tmp_cov.append(np.log(covTweet+epsilon_2))
                elif cov_name == 'No. of Tweets (state total)':
                    nrmlCnst = 100000. # per 100000 pop.
                    state = name[-2:] # state of the county
                    counties_fips = mapping[state].keys() # FIPS of all counties in this state
                    tweetPop = 0.
                    num_tweets = 0.
                    for county_fips in counties_fips:
                        collegeFrac = CntData[county_fips]['Bachelor\'s degree or higher, percent of persons age 25+, 2009-2013']/100.
                        collegeplus = 0.3 # frac of adults with a college degree or more using Twitter from Pew
                        collegeminus = 0.2 # frac of adults (0.16+0.24)/2 with less than a college degree using Twitter from Pew
                        tweetPop += (CntData[county_fips]['Population, 2014 estimate'] *
                                     (collegeFrac*collegeplus + (1.-collegeFrac)*collegeminus))
                        num_tweets += CntData[county_fips]['No. of Tweets'][w_end.strftime('%m/%d/%Y')]
                    covTweet = nrmlCnst*(num_tweets)/tweetPop
                    tmp_cov.append(np.log(covTweet+epsilon_2))
                elif cov_name == 'Vaccination percentage %':
                    # numbe of unvaccinated Medicare recipients as a factor of (approx.) total population
                    covVacc = ((1.0-CntData[fips]['Vaccination percentage %'][w_end.strftime('%m/%d/%Y')]/100.) *
                        (CntData[fips]['Persons 65 years and over, percent, 2013']/100.)) # between 0 and 1
                    tmp_cov.append(np.log(np.divide(covVacc+epsilon_3,1-covVacc+epsilon_3)))
                elif cov_name == 'Population per square mile, 2010':
                    # normalized population density
                    nrmlCnstDen = 100.
                    covPopden = (CntData[fips]['Population per square mile, 2010'] / nrmlCnstDen)
                    tmp_cov.append(np.log(covPopden+epsilon_4))
                else:
                    tmp_cov.append(CntData[fips][cov_name])
                    print cov_name
            
            Covariates[num_counties*wk+CountyName[name][0],] = tmp_cov            
            
            '''
            Covariates[num_counties*wk+CountyName[name][0],] = (
                CntData[fips]['No. of Tweets'][w_end.strftime('%m/%d/%Y')],
                CntData[fips]['Population per square mile, 2010']/10.)
            '''
            '''
            # Other variables of interest
            OtherVar[num_counties*wk+CountyName[name][0],] = (
                CntData[fips]['Population, 2014 estimate'],
                CntData[fips]['High school graduate or higher, percent of persons age 25+, 2009-2013'],
                CntData[fips]['Bachelor\'s degree or higher, percent of persons age 25+, 2009-2013'],
                CntData[fips]['Persons 65 years and over, percent, 2013'],
                CntData[fips]['Persons under 18 years, percent, 2013'],
                CntData[fips]['Per capita money income in past 12 months (2013 dollars), 2009-2013'])
            '''
        wk = wk + 1 # counter
        w_end = w_end + timedelta(days=7) # date

    if smooth is not None:
        for cov_name, method in smooth.items():
            for county in range(num_counties):
                Covariates[county::num_counties,CovName.index(cov_name)] = SmoothMethod[method[0]](
                Covariates[county::num_counties,CovName.index(cov_name)], **method[1])

    # transform the range of covariates to -\infty to \infty
    #Covariates = np.array((np.log(Covariates[:,0]+epsilon_2),
    #    np.log(np.divide(Covariates[:,1]+epsilon_3,1-Covariates[:,1]+epsilon_3)),
    #    np.log(Covariates[:,2]+epsilon_4))).T
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
