#Proposal: Challenge Problem 7, Phase 3

##Summary

Participating teams’ models failed to produce reconstruction results during Phase 1 that would allow for the real-time predictions planned for Phase 2. However, the flu-spread prediction problem is a rich domain for incremental model development using a variety of data sources. The flu-spread problem is representative of a wide range of real-world modeling and prediction problems involving spatiotemporal data from multiple sources. It also invites the integration of well-studied deterministic differential equation models of epidemics. Challenge Problem 7 represents an opportunity to show that probabilistic programming languages can enable rapid, iterative development of predictive models that include these kinds of data and deterministic models.

Phase 1 results show that, in populations of sufficent size, tweet counts correlate well with both Medicare vaccination counts early in the flu season and ILINet rates later in the season.


##Possible new ingredients

- ILINet surveillance data is available from 1997 onward. In Phase 1, only the 2013-2014 season was provided as training data. 
- Historical Twitter data is available for previous seasons.
- Google Flu Trends: 2008 US flu spread model updated in 2009, 2013, and 2014. Model output is publicly available for all four versions, with estimated weekly rates for all 10 HHS regions, all 50 states, and 96 US cities.
- Standard compartmental models in epidemiology, especially SIR and its extensions to accomodate vaccination, incubation delay, and age-group contact probabilities.
- Publicly available localized daily temperature and precipitation data from NOAA. Because flu rates show a strong seasonal fluctuation, it may be interesting to correlate infection patterns with fine-grained weather data.
- Public elementary and high schools are required to collect and report daily student attendance rates. This data is publicly available through the US Department of Education and the National Center for Education Statistics, although typically not as a time-series. However, daily or weekly attendance rates may be available from some state education departments or school districts. If available at the school district level,  attendance data may indicate ILI in the general population with with high spatial resolution.


##Possible problem extensions

- Incorporate additional data for model training or observations.
- Add a deterministic component (SIR or related model) using an ODE solver or numerical simulation.
- Gradual approach: first model a single population without spatial structure. The entire US is a logical starting point, since we have relatively smooth data and complete ground truth. Then adapt the US model to individual HHS regions, and then to states. Attempt to isolate parameters that can be tuned to reproduce regional variations. If this is possible, can these models make predictions for populations where Twitter data is sparse or noisy?
- The A/H1N1 ("swine flu") epandemic of 2009 is an especially interesting target for simulated forecasting as it had a double peak, with the second peak of unusually high magnitude, and was out of sync with the usual seasonal fluctuation. How far in advance can a general model for the US predict this kind of behavior?
- Encourage iterative development by providing a sequence of intermediate goals or mileposts, rather than a single monolithic deliverable.
- Different approaches to a fine-grained spatial model are possible. For example, rather than binning geolocated tweets into counties, we could use the lat/lon coordinates directly in a continuous plane, allowing spatial population clusters to emerge.
- Simulate nowcasting for multiple seasons of historical data. If this is accomplished and produces good results, a follow-up goal could be efficient daily prediction using streaming Twitter data, as in Phase 2.
