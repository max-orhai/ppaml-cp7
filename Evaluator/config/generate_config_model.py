#!/usr/bin/env python

# Copyright (c) 2015-2016 MIT Probabilistic Computing Project.
# Released under the MIT License; refer to LICENSE.txt.

import json
import sys

from parsable import parsable

DEFAULT_CROSSCATTS = {
    'forecast_model'            : ('crosscatts', str),
    'lag'                       : (10, int),
    'mh_chains'                 : (15, int),
    'mh_iterations_incremental' : (100, int),
    'mh_iterations_initial'     : (1000, int),
    'samples_prediction'        : (50, int),
    'seed'                      : (1, int),
}

# The main entries of this dictionary are `"forecast_model"` and
# `"source_kernel"`, which must be specified in tandem. The following pairs of
# entries are allowed:

# forecast_model   | source_kernel
# --------------   | -------------
# `"gp_se+wn"`     | `"gps/gausproc_se.vnts"`
# `"gp_per+wn"`    | `"gps/gausproc_per.vnts"`
# `"gp_seXper+wn"` | `"gps/gausproc_seXper.vnts"`
# `"gp_se+per+wn"` | `"gps/gausproc_se_per.vnts"`


DEFAULT_GAUSPROC = {
    'forecast_model'            : ('gp_se+wn', str),
    'mh_chains'                 : (15, int),
    'mh_iterations_incremental' : (50, int),
    'mh_iterations_initial'     : (1000, int),
    'samples_prediction'        : (50, int),
    'seed'                      : (1, int),
    'source_inference'          : ('gps/gausproc_inference.vnts', str),
    'source_kernel'             : ('gps/gausproc_se.vnts', str),
    'source_prior'              : ('gps/gausproc_prior.vnts', str),
    'source_utils'              : ('gps/gausproc_utils.vnts', str),
}

DEFUALT_VENTURE_DSM = {
    'forecast_model'            : ('venture_dsm', str),
    'mh_chains'                 : (10, int),
    'mh_iterations_incremental' : (10, int),
    'mh_iterations_initial'     : (1, int),
    'samples_prediction'        : (50, int),
    'seed'                      : (1, int),
    'source_inference'          : ('venture_domain_specific/dsm_inference.vnts', str),
    'source_function'           : ('venture_domain_specific/dsm_function.vnts', str),
    'source_prior'              : ('venture_domain_specific/dsm_prior.vnts', str),
    'source_utils'              : ('venture_domain_specific/dsm_utils.vnts', str),
}

def get_default(kwargs, default, key):
    if key not in kwargs:
        return default[key][0]
    tpe = default[key][1]
    return tpe(kwargs[key])


def write_config(defaults, **kwargs):
    config = {
        key: get_default(kwargs, defaults, key)
        for key in defaults
    }
    stream = kwargs.get('stream', sys.stdout)
    json.dump(config, stream, indent=2)
    stream.write('\n')

@parsable
def gausproc(**kwargs):
    """Generate configuration for gausproc models.

    The allowed keys and defaults are in show in the DEFAULT_GAUSPROC dictionary
    at the top of this module. They can be overridden using key=val as shown
    below:

    ./generate_config_model gausproc mh_chains=10
    """
    write_config(DEFAULT_GAUSPROC, **kwargs)

@parsable
def crosscatts(**kwargs):
    """Generate configuration for crosscatts models.

    The allowed keys and defaults are in show in the DEFAULT_CROSSCATTS
    dictionary at the top of this module. They can be overridden using key=val
    as shown below:

    ./generate_config_model crosscatts mh_chains=15
    """
    write_config(DEFAULT_CROSSCATTS, **kwargs)

@parsable
def venture_dsm(**kwargs):
    """Generate configuration for venture domain specific model.

    The allowed keys and defaults are in show in the DEFUALT_VENTURE_DSM
    dictionary at the top of this module. They can be overridden using key=val
    as shown below:

    ./generate_config_model venture_dsm mh_chains=10
    """
    config = {
        key: get_default(kwargs, DEFUALT_VENTURE_DSM, key)
        for key in DEFUALT_VENTURE_DSM
    }
    stream = kwargs.get('stream', sys.stdout)
    json.dump(config, stream, indent=2)
    stream.write('\n')


if __name__ == '__main__':
    parsable()
