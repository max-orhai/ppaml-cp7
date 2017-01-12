#Proposal: Challenge Problem 7, Phase 3

##Summary

Participating teams’ models failed to produce reconstruction results with acceptable accuracy during Phase 1 that would allow for the real-time predictions planned for Phase 2. Nevertheless, Phase 1 results show that, in populations of sufficent size, tweet counts correlate well with both Medicare vaccination counts early in the flu season and ILINet rates later in the season. From our observation, we believe the causes for low accuracy can be attributed to unfamiliarity of the problem and model, and limited time to construct and test the implemented model. Another factor is the limited amount of data (number of years where data is available) and data sources to achieve good accuracy. We attempt to address those issues in Phase 3 by providing additional data, encouraging experimenting alternative models and improving the evaluation process.

The flu-spread prediction problem is a rich domain for incremental model development using a variety of data sources. The flu-spread problem is representative of a wide range of real-world modeling and prediction problems involving spatiotemporal data from multiple sources. It also invites the integration of well-studied deterministic differential equation models of epidemics. Challenge Problem 7 represents an opportunity to show that probabilistic programming languages can enable rapid, iterative development of predictive models that include these kinds of data and deterministic models.



##Possible new ingredients

- ILINet surveillance data is available from 1997 onward. In Phase 1, only the 2013-2014 season was provided as training data. 
- Historical Twitter data is available for previous seasons.
- Google Flu Trends: 2008 US flu spread model updated in 2009, 2013, and 2014. Model output is publicly available for all four versions, with estimated weekly rates for all 10 HHS regions, all 50 states, and 96 US cities.
- Standard compartmental models in epidemiology, especially SIR and its extensions to accomodate vaccination, incubation delay, and age-group contact probabilities.
- Publicly available localized daily temperature and precipitation data from NOAA. Because flu rates show a strong seasonal fluctuation, it may be interesting to correlate infection patterns with fine-grained weather data.
- Public elementary and high schools are required to collect and report daily student attendance rates. This data is publicly available through the US Department of Education and the National Center for Education Statistics, although typically not as a time-series. However, daily or weekly attendance rates may be available from some state education departments or school districts. If available at the school district level,  attendance data may indicate ILI in the general population with with high spatial resolution. (Question: how timely are the data published?)


##Possible problem extensions

- Incorporate additional data for model training or observations. Take advantage the power of the Probabilistic Programming languages to quickly experiment on the predictive power or complementary effects of new data sources.

- Explore different model structures:
  - Add a deterministic component such as SIR or other commonly used epidemic models
  - Hierarchical model approach: Treat the US, HHS regions, states and counties as separate levels in a hierarchical model, and then capture the contributions of various data sources on predicting regional variations. A potential benefit of this approach is that sparse fine-grained Twitter data from areas of low population densities don't negatively impact on the accuracy of larger-scale ILI trends.
  - Incorporate explicit multi-modal temporal effects: Due to different virus strains and other effects, the ILI ratesin a flu season sometimes exhibit two peaks. The A/H1N1 ("swine flu") epidemic of 2009 is an especially interesting target for simulated forecasting as it had a double peak, with the second peak of unusually high magnitude, and was out of sync with the usual seasonal fluctuation. A deterministic multi-modal model component to explicitly capture such characteristics is expected to improve the temporal prediction accuracy.
  - Different approaches to a fine-grained spatial model: For example, rather than binning geolocated tweets into counties, we could use the lat/lon coordinates directly in a continuous plane, allowing spatial population clusters to emerge.

- Improve testing and evaluation process
  - Encourage iterative development by providing a sequence of intermediate goals or mileposts, rather than a single monolithic deliverable. For example, a performer may first deliver results using a small subset of data sources in a smaller geographical area or in a coarser spatial resolution (e.g. state). If the results are reasonable, the performer can then follow by incorporating more data sources and modeling at a higher resolution or in a larger region.
  - Simulate nowcasting for multiple seasons of historical data. If this is accomplished and produces good results, a follow-up goal could be efficient daily prediction using streaming Twitter data, as in Phase 2.
