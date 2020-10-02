# Continuum Deployer

## Setup
Install dependencies
```shell
pip install -r requirements.txt
# or
make install-req
```

## Runs tests
```shell
pytest
```

## Release
Build python package 

```shell
python setup.py bdist_wheel
# or
make dist
```

## Clean workspace
Remove compiled python files and remove build resources.

```shell
make clean-pyc
make clean-build
```

## Usage

### General
```
Usage: app.py [OPTIONS] COMMAND [ARGS]...

  Prototypical Continuum Computing Deployer

Options:
  --help  Show this message and exit.

Commands:
  match
  parse-resources
  print-resources
```

### Matching
```
Usage: app.py match [OPTIONS]

Options:
  -r, --resources TEXT       Path to resources file  [required]
  -d, --deployment TEXT      Path to DSL file  [required]
  -t, --type [helm]          Deployment DSL type (default: helm)
  -s, --solver [sat|greedy]  Solver to match deployments to resources
  --help                     Show this message and exit.
```

## Plugins

The Continuum Deployer supports a plugin interface for the core components of the workload handling process.

DSL importers and exporters as well as the actual placement solvers are pluggabel and custom implementations can easily be added by the user.

Plugins in the default plugins directory, which resides under `continuum_deployer/plugins`, are loaded automatically. Plugin directories outside of the module can be added via the command line parameter `-p/--plugins`.

The Continuum Deployer uses the lightweight Python plugin library [`Yapsy`](http://yapsy.sourceforge.net/) to implement the plugin loading and handling.

Need to follow some requirements in order to be successfully loaded. A well formed Continuum Deployer plugin consists of the following two files:

1. Plugin Info - `<name>.yapsy-plugin`
```
[Core]
Name = <Name of the Plugin>
Module = <Name of the python module file>

[Documentation]
Description = <Description which is used to display information to the user>
```

2. Plugin Implementation - `<name>.py`
```
class Name(<Importer/Exporter/Solver>):
    pass
```

The plugin implementation need to inherit form one of the supported Continuum Deployer interfaces:
```
from continuum_deployer.dsl.importer.importer import Importer
from continuum_deployer.dsl.exporter.exporter import Exporter
from continuum_deployer.solving.solver import Solver
```

Trough the interactive CLI the different loaded plugins are frictionless displayed for selection at the appropriate process step.

## Limitations

### Helm
- Kubernetes Resources Limits are parsed and available in via the internal deployment object structure but are currently not considered by the included solvers
- Memory requirements for a single deployment that are smaller than 1 MB are currently replaced by 0 and placed without size considerations by the solvers

## Authors

- @hassdan1 - Daniel Haß