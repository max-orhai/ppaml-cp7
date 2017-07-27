# MIT solution configurations

This table summarizes all changes made to the submitted MIT solution in the process of evaluating each model.
The JSON files used by the *crosscatts* and *dsm* models are the output of generate_config_model.py.

| model | as submitted | as evaluated | diff |
| ----- | ------------ | ------------ | ---- |
| *per* | Dockerfile.full | Dockerfile.eval-per | Dockerfile.full--eval-per.diff |
| *se*  | -- | Dockerfile.eval-se | Dockerfile.full--eval-se.diff |
| *crosscatts* | Dockerfile.full2,  config-crosscatts.json | Dockerfile.eval2, config-crosscatts.json | Dockerfile.full2--eval2.diff |
| *dsm* (attempts) | Dockerfile.full2, config-dsm.json | Dockerfile.eval2, config-dsm.json | Dockerfile.full2--eval2.diff |
| *dsm* (success) | -- | Dockerfile.eval2, config-dsm-MINIMAL.json | Dockerfile.full2--eval2.diff, config-dsm--dsm-MINIMAL.json.diff |
