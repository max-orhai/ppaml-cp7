# Running the MIT team submission

This document contains a description of the following items:

1. Procedure for installing Venture and associated dependencies required by our
   scripts.

2. Documentation of the command-line interface for the scripts in this
   submission, and their expected inputs and outputs.

3. Examples of running our scripts on the 2014/2015 flu season (via Docker).

## Cloning this repository.

To clone this repository correctly (including git submodules), please follow
these steps:

    $ git clone git@github.com:probcomp/ppaml-cp7.git
    $ cd ppaml-cp7
    $ git submodule update --init

Confirm that [modules/Venturecxx](modules/Venturecxx) and
[modules/parsable](modules/parsable) are both non-empty directories.

## Installing Venture and dependencies via Docker

All `docker` commands are tested on Docker version 1.12.6.

The main dependencies of our submission are
[Venturecxx](https://github.com/probcomp/Venturecxx) and
[cgpm](https://github.com/probcomp/cgpm) , which we have included in this
repository as a submodule in [modules](modules). Both cgpm and Venturecxx depend
on standard libraries from Ubuntu apt.

To best describe the installation procedure, we have documented the exact steps
to install Venturecxx/cpgm in a fresh version of Ubuntu 16.04 as a Dockerfile.
These steps are shown in [docker/setup/Dockerfile](docker/setup/Dockerfile),
which should be built (from the root of this repository) using:

    $ docker build -f docker/setup/Dockerfile -t probcomp/venture:20170709 .

Note that that the name of the tag `probcomp/venture:20170709` is important, so
please use this tag as shown. This Dockerfile:

 - retrieves packages from apt;
 - configures `matplotlib` and `OpenBLAS` correctly;
 - copies [this repository](https://github.com/probcomp/ppaml-cp7) into the image;
 - installs the Venturecxx and parsable python libraries in the [](modules)
   directory.

We have tested this image and recommend using it to evaluate our submission. If
these steps are instead going to be reproduced in an Ubuntu 16.04 installation
but outside of Docker, please make sure to run them exactly as shown in
[](docker/setup/Dockerfile).

__Important__: Ensure to set the environment variable `export
OPENBLAS_NUM_THREADS=1` before running any of our scripts.

## Command-line interfaces for solution scripts

All the scripts that comprise our solution live in [](scripts/).

__Important__: These scripts assume that the invoker's working directory is
[](scripts/). They should not be executed from any other directory.

We now describe the main scripts that comprise our solution:

### [](scripts/launcher.py)

This script is used to create the forecasts from a `week-n.txt` file. Its usage
is as follows:

    $ ./launcher.py -h
    usage: launcher.py [-h] [-p PARALLELISM]
                       config_population config_model data_dir models_dir
                       week_file

    positional arguments:
      config_population     Path of configuration file for populations to
                            forecast.
      config_model          Path of configuration file for model to use for
                            forecasting.
      data_dir              Path of directory of flu and associated csv files.
      models_dir            Path of the directory of stored models.
      week_file             Path of the week file to use for forecasting.

    optional arguments:
      -h, --help            show this help message and exit
      -p PARALLELISM, --parallelism PARALLELISM
                            Number of jobs to run in parallel.

- The `data_dir` argument specifies directory like the provided [](data/) in
  this repository. It contains all the `*-flu.csv` and other files.

- The `models_dir` argument specifies a directory name where the intermediate
  models will be stored, for example [data/models](data/models). This directory
  should exist in the filesystem.

- The `week_file` argument specifies a week file such as
  [data/weeks/week-2014.42.txt](data/weeks/week-2014.42.txt) which contains the
  latest rows.

  __Important__: our submission requires that any rows in `week-n.txt` do not
  already exist in the corresponding .csv file from `data_dir`. For example if
  `week-2014.42.txt` contains the following row:

  ```
  >> USA-weather.csv
  2014.21,18.82,7.83,3.36,18.25,7.48,2.53,19.02,7.58,1.83,24.47,12.53,0.86,20.09,8.10,2.22,27.57,15.16,1.16,24.73,11.68,1.84,20.72,6.13,1.72,24.37,10.08,0.52,19.63,6.74,1.42,22.72,10.00,1.54
  ```

  Then `data_dir/USA-weather.csv` should not have an entry for `2014.21`.

- The `-p <num_cores>` argument specifies the number of time-series to predict
  in parallel. While it can be safely set to 1 (by default), we will describe
  later how to set this flag for best results.

- The `config_population` and `config_model` arguments are described in the next
  section.

Invoking `launcher.py` will generate a file named
`forecast-[<forecast_model>]-n.txt` in the same directory as the `week-n.txt`
file. The suffix `forecast_model` is determined by the choice of model in
`config_model` (documented below).

The script will also produce several `.json` files in `models_dir` which are
cached models to be loaded for future invocations of `./launcher.py`.

### [scripts/generate_config_population.py](scripts/generate_config_population.py)

This script produces the configuration file for the `conf_population` arguemnt
which is required by `launcher.py`. Its output (to stdout) specifies which
time-series to forecast, as follows;

    $ ./generate_config_population.py
    {
      "forecast_num_weeks"   : 4,
      "forecast_populations" : [
        {
            "target"               :  ["USA-flu.csv", "R04.%ILI"],
            "covariates"           :  [
                                        ("USA-tweets.csv", "R04"),
                                        ("USA-weather.csv", "R04.Tmin")
            ],
            "start_train"          :  2009.01,
        },
        {
            "target"               :  ["TN-flu.csv", "TN.%ILI"],
            "covariates"           :  [
                                        ("TN-tweets.csv", "TN.tc"),
                                        ("TN-weather.csv", "TN.Tmin")
            ],
            "start_train"          : null,
        },
        {
            "target"               :  ["TN-flu.csv", "D10.%ILI"],
            "covariates"           :  [
                                        ("TN-tweets.csv", "D10.tc"),
                                        ("TN-weather.csv", "D10.Tmin")
            ],
            "start_train"          : null,
        }
      ]
    }

The entry `"forecast_num_weeks"` tells `launcher.py` how many weeks in the
future to predict after reading `week-n.txt`. For example, if
`"forecast_num_weeks" : 4`, the generated forecast file for `week-2014.40.txt`
will have predictions for weeks `2014.40, 2014.41, 2014.42, 2014.43, 2014.44`.
Note if `"forecast_num_weeks" : 0` then only a prediction for `2014.40` will be
produced (a. nowcast).

The entry `"forecast_population"` contains a list of dictionaries. Each
dictionary specifies a time series to predict. The keys of these dictionaries
are:

- `"target"`; the value is a tuple where the first item is the name of the
  `.csv` file in `data_dir`, and the second item is the name of the column in
  that csv file.

- `"covariates"`: A list of tuples, each tuple contains a csv/column pair
  analogous to the tuple for `"target"`.

- `"start_train"`: A float (in week format), specifying where to start the
  training set (earlier dates are discarded). This is key is useful for trimming
  very long timeseries such as `USA-flu:USA.%ILI` and speeding up inference. An
  entry of `None` (in python) or `null` (in json) means to use the entire time
  series for training.

__Important__: The
[generate_config_population](scripts/generate_config_population.py) file that is
checked-in contains entries for the four required populations. To evaluate our
solution on all the available flu series, just add the corresponding entries
into the `"forecast_population"` list and regenerate the file.

### [scripts/generate_config_model.py](scripts/generate_config_model.py)

This script produces the configuration file for the `conf_module` argument which
is required by `launcher.py`. Its output (to stdout) specifies which modeling
strategy to use for the forecasting. There are currently three different models,
`gausproc`, `crosscatts` and `venture_dsm `, each documented below:

#### crosscatts

    $ ./generate_config_model.py crosscatts
    {
      "forecast_model": "crosscatts",
      "lag": 10,
      "mh_chains": 18
      "mh_iterations_incremental": 100,
      "mh_iterations_initial": 1000,
      "samples_prediction": 50,
      "seed": 1,
    }


- The `"forecast_model"` entry tells the launcher to use `crosscatts`, a variant
  of CrossCat adapted for modeling panel data.

- The `"lag"` entry specifies how many observations to use in a single sliding
  window for CrossCat.

#### venture_dsm

    $ ./generate_config_model.py venture_dsm
    {
        "forecast_model"            : ("venture_dsm", str),
        "mh_chains"                 : (20, int),
        "mh_iterations_incremental" : (10, int),
        "mh_iterations_initial"     : (1, int),
        "samples_prediction:        : (50, int),
        "seed"                      : (1, int),
        "source_inference"          : ("venture_domain_specific/dsm_inference.vnts", str),
        "source_function"           : ("venture_domain_specific/dsm_function.vnts", str),
        "source_prior"              : ("venture_domain_specific/dsm_prior.vnts", str),
        "source_utils"              : ("venture_domain_specific/dsm_utils.vnts", str),
    }

- The `"forecast_model"` entry tells the launcher to use a venture-based domain
  specific model. At the moment, this model ignores the previous years and tries
  to fit a "peak" to the current year. This is an initial version and will be
  extended to include information from previous years and potentially
  covariates.

- The `"source_function"` entry tells the launcher about a path the venture
  program modelling the peak.

- The `"source_prior"` entry tells the launcher about a path the venture
  program defining the prior over model parameters.

#### gausproc

    $ ./generate_config_model.py gausproc
    {
      "forecast_model"            : "gp_se+wn",
      "mh_chains"                 : 15,
      "mh_iterations_incremental" : 50,
      "mh_iterations_initial"     : 1000,
      "samples_prediction"        : 50
      "seed"                      : 1,
      "source_inference"          : "gps/gausproc_inference.vnts",
      "source_kernel"             : "gps/gausproc_se.vnts",
      "source_prior"              : "gps/gausproc_prior.vnts",
      "source_utils"              : "gps/gausproc_utils.vnts",
    }

- The `"forecast_model"` and `"source_kernel"` entries are the main keys, which
  must be specified in tandem. The following pairs are allowed:

  forecast_model   | source_kernel
  --------------   | -------------
  `"gp_se+wn"`     | `"gps/gausproc_se.vnts"`
  `"gp_per+wn"`    | `"gps/gausproc_per.vnts"`
  `"gp_seXper+wn"` | `"gps/gausproc_seXper.vnts"`
  `"gp_se+per+wn"` | `"gps/gausproc_se_per.vnts"`

  __Important__: Our preference is to use `"forecast_model": "gp_se+wn"` with
  `"source_kernel":"gps/gausproc_se.vnts"`. If there is no trouble with running
  our submission, please evaluate all four forecasting models shown in the table
  above as well.

#### Other parameters

- The `"mh_chains"` entry specifies how many MCMC chains to run in parallel. We
  have set a default value of 15. We suggest to use this value to determine the
  argument of `-p <num_cores>` in `./launcher.py`. For example, on a 64 core
  server, we set `-p 4` which results in a total of 60 cores used at any given
  time: 15 cores per job (1 core per MCMC chain), and 4 jobs in parallel = 60
  cores. Running more jobs than available cores is likely to significantly slow
  down the process, so please set this flag appropriately.

- The `"mh_iterations_initial"` and `"mh_iterations_incremental"` keys specify
  how many steps of MH to run (i) for the initial training, and (ii) for
  training in between forecasts (i.e. each time a new `week-n.txt` file is
  introduced), receptively.

- The `"samples_prediction"` key specifies how many samples to generate for
  computing the mean prediction.

## Examples of running our solution in Docker

We have provided two Dockerfiles which show how to invoke the three scripts
described above. The `<forecast_model>` argument can be `gausproc`,
`crosscatts`, or `venture_dsm`.

- [docker/crash/Dockerfile](docker/crash/Dockerfile) contains a basic crash
  test. It shows how to use `launcher.py`, `generate_config_model.py,` and
  `generate_config_population.py` for forecasting on two weeks. Please refer to
  the docker file for further details.

  This image can be built from the project root with:

  ```
  $ docker build -f docker/crash/Dockerfile --build-arg forecast_model=<forecast_model> -t probcomp/ppaml-cp7-crash:20170709 .
  ```

  The build process is expected to take < 2 minutes on a 64 core server.

- [docker/full/Dockerfile](docker/full/Dockerfile) contains a full run of our
  baseline solution on weeks 2014.40 through 2015.20, which is created as a
  dummy "evaluation set".  Please refer to the docker commands for further
  details.

  This file can be built from the project root with:

  ```
  $ docker build -f docker/full/Dockerfile --build-arg forecast_model=<forecast_model> -t probcomp/ppaml-cp7-full:20170709 .
  ```

  The build process is expected to take roughly 1 hour on a 64 core server.


Note that the above two images require `docker/setup/Dockerfile` to have been
built with the tag `probcomp/venture:20170709` as described in the "Installing
Venture and dependencies via Docker" section.

The forecasts will be placed in `/ppaml-cp7/2014-season/weeks`. Plots of the
predictions and `.gif` animations will be in placed in
`/ppaml-cp7/2014-season/plots`.

After building a docker image, it can be explored in an interactive terminal:

    $ docker run -it probcomp/ppaml-cp7-full:20170709 /bin/bash

Files in a docker image can be copied to the host machine:

    $ docker run --rm probcomp/ppaml-cp7-full:20170709 tar -C / -cv ppaml-cp7 > venture-cp7.tar.gz
