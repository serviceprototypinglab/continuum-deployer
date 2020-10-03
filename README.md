# Continuum Deployer

## General

The Continuum Deployer is a prototypical implementation of a resource matching system that allows a user to interactively participate in the resource placement process. The user is able to change and adopt the placement and options interactively during the matchmaking process.

The Continuum Deployer supports the digestion of local, templated or packaged Helm Charts out-of-the box. Additionally two solvers are shipped within the module (Greedy and SAT solver). The final resource placement can be viewed interactively but also exported trough the built-in Kubernetes exporter to a deployable Kubernetes manifest.

To extent and adopt the Deployer the module offers a rich plugin interface that allows users to add custom version of the previously mentioned components in order do get even better results with regard to their infrastructure and requirements. Please find details in the [Plugins](#Plugins) section.

## Screenshots

To give potential users an idea of how the interactive process looks like you can find a collection of screenshots below:

1. Resource Parsing

![Resource Parsing](misc/screenshots/resource_parsing.jpg?raw=true "Resource Parsing")

2. Interactive Option Selection

![Interactive Option Selection](misc/screenshots/option_selection.jpg?raw=true "Interactive Option Selection")

3. Interactive evaluation of matching results

![Matching Results](misc/screenshots/matching_results.jpg?raw=true "Matching Results")

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

### Resources Definition

The Continuum Deployer digests a simple non-standard resources definition file as input for the matchmaking process.

Please find below an example for a simple resource file:
```
# name: String - Name of node
# cpu: int or float - Number of CPUs
# memory: int - Memory size in Megabyte (smallest node size support 1MB)
# labels: List - List of labels that are attached to the node

resources:
  - name: node-1
    cpu: 2
    memory: 8000
  - name: node-2
    cpu: 3
    memory: 3000
  - name: node-3
    cpu: 4
    memory: 4000
    labels:
      cloud: public
```

### Labels

Labels are the central mean within the Continuum Deployer for the user to express certain constraints with regard to the deployment placement. Each `node` and `workload` can be assigned with zero to as many labels as the user desires. A suitable `node` must possess all of the `workloads` labels or more to be considered for a deployment. Unlabeled `workloads` are able to run on any of the available nodes.

### Matching
```
Usage: app.py match [OPTIONS]

  Match deployments interactively

Options:
  -r, --resources TEXT   Path to resources file
  -d, --deployment TEXT  Path to DSL file
  -t, --type [helm]      Deployment DSL type
  -p, --plugins TEXT     Additional plugins directory path
  --help                 Show this message and exit.
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

An example for a prototypical plugin implementation can be found in the examples directory under `examples/plugins`.

## Limitations

### Helm
- `Kubernetes Resources Limits` are parsed and available in via the internal deployment object structure but are currently not considered by the included solvers
- `Memory requirements` for a single deployment that are smaller than 1 MB are currently replaced by 0 and placed without size considerations by the solvers
- `Standalone Pods` are currently not supported by the Helm DSL importer
- `DaemonSets` are currently not supported in their intended way (see [Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) for details). Currently the Continuum Deployer handles DaemonSets in a standalone fashion as single deployable unit.

## Authors

- @hassdan1 - Daniel Haß