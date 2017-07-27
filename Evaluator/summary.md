# CP7 results to date (26 July 2017)

[(Problem statement and data set)](https://github.com/GaloisInc/ppaml-cp7/tree/2e2d30f92ab6560cf61b4eef1989c519e40257c0)


## The solutions

Galois has received two sets of CP7 solutions from MIT.
The [first batch](https://github.com/probcomp/ppaml-cp7/blob/59e01e26041816296d73ea0b19043f5ae387fe9b/INSTALLING.md) included *se* and *per* models in Venture (described below), as well as two different combinations of those two models, *se+per* and *seXper*.
The combinations are not shown here since their results were very similar to the *per* model.

- *per*: a periodic gaussian process model (with added white noise) on a yearly cycle

- *se*: a squared-exponential gaussian process model, also with white noise

Neither of these initial models' forecast accuracy was satisfactory.
The subsequent [revision](https://github.com/probcomp/ppaml-cp7/blob/20170707-fsaad-dpmm/INSTALLING.md) included two new models:

- *crosscatts*: a version of Crosscat specialized for multivariate time-series data

- *dsm*: a Venture domain-specific model which attempts to find a seasonal peak

The *crosscatts* model used minimum temperature and tweet-count covariates.
None of the other models used covariate data.

For comparison purposes, we have three other models:

- *fbprophet*: an open-source general-purpose [trend prediction](https://facebookincubator.github.io/prophet/) package released by Facebook, which wraps a 40-line Stan model

- *constant*: always predicts that future ILI rates will be the same as the last observed (two-week-old) rate

- *linxtrp*: linear extrapolation based on the average ILI rate increase or decrease over the last three observations


## Performance

Each of the MIT model took over an hour to run on an 8-core server instance.
Despite several tries, we have not been able to run the *dsm* model to completion using the [recommended settings](https://github.com/probcomp/ppaml-cp7/blob/20170707-fsaad-dpmm/INSTALLING.md#venture_dsm) of the parameters governing inference.
Although the solution does not run out of memory, it gets stuck mid-season.
The *dsm* results shown below were obtained using minimal inference parameter settings.

The *fbprophet* model runs on a laptop in about 2 minutes per population, without optimization.
The *constant* and *linextrp* models' runtimes are negligible.


## Forecasts over target season

Each model was run with a five-week forecast period, including the current (zero) week as a nowcast.
Forecast accuracy was evaluated for each model, and for each of these five weeks over the whole season.

| USA | R04 | TN | D10 |
| --- | --- | -- | --- |
| Entire continental US | HHS Region 4 (Southeast US) | Tennessee state | Knox county, TN

---
### MIT *per* model
(Only evaluated in Region 4)
![per forecast animation](results/per.gif)
![per MSE](results/per.png)

---
### MIT *se* model
(The team's preferred solution)
![se forecast animation](results/se.gif)
![se MSE](results/se.png)

---
### MIT *crosscatts* model
(Not evaluated in *USA* population)
![crosscatts forecast animation](results/crosscatts.gif)
![crosscatts MSE](results/crosscatts.png)

---
### MIT *dsm* model
(Not evaluated in *USA* population)
![dsm forecast animation](results/dsm.gif)
![dsm MSE](results/dsm.png)

### *fbprophet* model
(Negative rates in the smaller populations may be due to very wide confidence intervals)
![fbprophet forecast animation](results/fbprophet.gif)
![fbprophet MSE](results/fbprophet.png)

---
### *constant* model
![constant forecast animation](results/constant.gif)
![constant MSE](results/constant.png)

---
### *linxtrp* model
(Badly affected by noise in the smaller populations!)
![linxtrp forecast animation](results/linxtrp.gif)
![linxtrp MSE](results/linxtrp.png)


## Model comparisons

The above MSE per forecast week accuracy metric is shown here for each evaluated model in the four target populations.

![USA comparison](results/USA.png)
![R04 comparison](results/R04.png)
![TN comparison](results/TN.png)
![D10 comparison](results/D10.png)
