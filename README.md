# Continuum Deployer

> This prototypical tool was initially written as part of the EVA 2 (Erweiterte Vertiefungsarbeit | extended specialization work) during the studies to receive the scientific degree _Master of Science_.

## General

The Continuum Deployer is a prototypical implementation of a resource matching system that allows a user to interactively participate in the resource placement process. The user is able to change and adopt the placement and options interactively during the matchmaking process.

The Continuum Deployer supports the digestion of local, templated or packaged Helm Charts out-of-the box. Additionally two solvers are shipped within the module (Greedy and SAT solver). The final resource placement can be viewed interactively but also exported trough the built-in Kubernetes exporter to a deployable Kubernetes manifest.

To extent and adopt the Deployer the module offers a rich plugin interface that allows users to add custom version of the previously mentioned components in order do get even better results with regard to their infrastructure and requirements. Please find details in the [Plugins](#plugins) section.

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

Please find below an example for a simple resource file, which can also be found under `examples/resources/default.yaml`:
```
# name: String - Name of node
# cpu: int or float - Number of CPUs
# memory: int - Memory size in Megabyte (smallest node size support 1MB)
# labels: List - List of labels that are attached to the node

resources:
  - name: node-1
    cpu: 2
    memory: 8192
  - name: node-2
    cpu: 3
    memory: 2048
  - name: node-3
    cpu: 4
    memory: 4096
    labels:
      cloud: public
```

### Labels

Labels are the central mean within the Continuum Deployer for the user to express certain constraints with regard to the deployment placement. Each `node` and `workload` can be assigned with zero to as many labels as the user desires. A suitable `node` must possess all of the `workloads` labels or more to be considered for a deployment. Unlabeled `workloads` are able to run on any of the available nodes.

> Remark for the built-in Helm importer: this importer uses the [`NodeSelector`](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) values as sources for the deployment labels as the often refered Kubernetes [Labels and Selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) are not a fit for our purposes, as they often are populated with many default information which do not reflect the use case for labeling in the Continuum Deployer.

### Matching

The main CLI interface of the Continuum Deployer can be invoked by the `match` command. All CLI parameter options are optional and are available for ease of use to make it possible for the user to skip some of the interactive steps trough preset parameters (e.g. on multiple consecutive invocations).

After inspection of the matching results the Continuum Deployer allows the user to alter the input specifications if desired so. The changes to the resources file will be written back to the input file and therefore are persistent. The changes to the DSL are only happening in-memory as the tool supports multiple input formats (e.g. archives) that are not easy to change on-the-fly.

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

### Built-in Solvers

#### Greedy

The built-in greedy solver asks the solver for a single optimization target. The options are as follows:
- CPU: sorts resources and workloads by the size of their CPU attribute for greedy matching
- Memory: sorts resources and workloads by the size of their memory attribute for greedy matching

The actual matching is carried out in a greedy matching: the largest workloads are probed for placement on a sorted list of resources. In this list resources appear in descending order based on the selected optimization target.

#### SAT (CP-SAT Solver using constraint programming)

The built-in CP-SAT solver offers multiple options with regard to the optimization target (in future version this options could be enhanced way further):
- Maximize idle CPU: solver tries to maximize idle cpu resources
- Maximize idle Memory: solver tries to maximize idle memory resources
- Minimize idle CPU: solver tries to minimize idle cpu resources
- Minimize idle Memory: solver tries to minimize idle memory resources
- Minimize idle Resources: solver tries to minimize idle resources (CPU+Memory)
- Maximize idle Resources: solver tries to maximize idle resources (CPU+Memory)

This solver uses constrained programming to define rules and constrains that describe the resource matching problem in mathematical terms. Afterwards this optimization is solved as optimal as possible.

The results of this solver differ from the greedy ones: if this solver cannot come up with an optimal solution the run will fail and all resources are displayed as unschedulable. This feasibility constraint is enforced on each label group (if labels are defined).

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

### Helm/Kubernetes
- `Kubernetes Resources Limits` are parsed and available in via the internal deployment object structure but are currently not considered by the included solvers.
- `Memory requirements` for a single deployment that are smaller than 1 MB are currently replaced by 0 and placed without size considerations by the solvers.
- `Standalone Pods` are currently not supported by the Helm DSL importer.
- `DaemonSets` are currently not supported in their intended way (see [Kubernetes docs](https://kubernetes.io/docs/concepts/workloads/controllers/daemonset/) for details). Currently the Continuum Deployer handles DaemonSets in a standalone fashion as single deployable unit.
- `Cluster awareness` is currently not implemented in the resource representation, solving and export functionality. But you are able to work around this with a set of properly labeled resources and deployments.
- [`NodeSelector`](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) annotations are used to enforce a certain resource placement. This is suboptimal as it works around the existing Kubernetes Scheduling intelligence, but necessary in order to facilitate the demo purpose of this tool. One idea to work around this limitation is the implementation of cluster awareness and ingesting whole Kubernetes clusters as resources instead of single nodes.
- `Non deployable Kubernetes API objects` are currently ignored by the Continuum Deployer which meight results in actually unusable deployments (e.g. due to missing objects like `Services` or `ConfigMaps`). At the current state of the tool this is somewhat intended as the actually deployment of the resources is currently not in the focus of the toolchain. Currently the Continuum Deployer focuses on the interactive resource matching and dynamic interaction with the scheduling process. The support for any/all Kubernetes API objects is left for an upcoming iteration of the tool.
  - Currently supported Kubernetes API objects: `Deployment`, `ReplicaSet`, `StatefulSet`, `DaemonSet`, `Jobs`, `CronJob`, `DaemonSet` (partially, see above)

### Resources
- Currently the only two resources considered for the placement are `CPU` and `Memory` requirements of the deployments. This can be enlarged in the future to other resources types like e.g. `Bandwidth` or `Cost` to make the placement even more precise.

## Internal Architecture

### General Matchmaking Flow

A general an full invocation of the Continuum Deployer traverses the following three stages to come up with a deployment proposal:
1. `Importer` - the selected `Importer` takes care of parsing the input DSL definition to the standardized Continuum Deployer internal object-based resource representation. These objects and their encoded information are the base for the following two stages. The output of the importer are propagated instances of the `DeploymentEntity` dataclass that holds the parsed values for the further processing.
- Target resources or nodes that should hold the deployments entities later on, are parsed by the non-pluggable `Resources` class
2. `Solver` - the selected `Solver` takes care of the actual decision making on which deployment will reside on which target resource. A `Matcher` run is invoked with list of `DeploymentEntity` and `ResourceEntity` objects that should get placed in this run. The `Matcher` requires the initialization with the full list of `DeploymentEntity` and `ResourceEntity` only for some pre-flight checks. To keep the actual solver implementation simple the handling of label constraints is currently externalized to the general `Matcher` class. The `Matcher` takes care of resources and deployment grouping with respect to the defined labels and calls the actual `Matcher`-implementation multiple times with different sets of deployments and resources.
3. `Exporter` - the selected `Exporter` takes care of writing the Continuum Deployer internal resources representation back to the desired and deployable output format. With the currently build-in Kubernetes manifest exporter the deployments will be exported and labeled with a specific `nodeSelector` (see [Kubernetes docs](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#nodeselector) for more information) that corresponds to the result of the matchmaking process.

### Pluggable Interfaces

Description of the interfaces that can be used to alter the Continuum Deployer via the plugin framework. The following classes should be inherited from and implement at minimum the described methods.

#### `Importer` - `from continuum_deployer.dsl.importer.importer import Importer`

- `_check_requirements(self)` - Can be implemented and used to check for external dependencies before the actual invocation
  - should raise a `continuum_deployer.utils.exceptions.RequirementsError` if requirements are violated
- `_gen_config(self)` - Can be implemented to define settings that can be altered by the user during runtime
  - should return a `continuum_deployer.utils.config.Config` object filled with the desired `SettingValues`
- `get_dsl_content(self, dsl_path)` - Must be implemented and return the plain string representation of the DSL resource
  - is used in order to be able to support different DSL formats like files, archives etc.
- `parse(self, dsl_input)` - Must be implemented and takes the formerly by `get_dsl_content` read DSL content and parses it to the object mapping
  - should return a list of `DeploymentEntity` objects

#### `Solver` - `from continuum_deployer.solving.solver import Solver`

- `_gen_config(self)` - Can be implemented to define settings that can be altered by the user during runtime
  - should return a `continuum_deployer.utils.config.Config` object filled with the desired `SettingValues`
- `do_matching(self, deployment_entities, resources)` - Must be implemented and takes a list of `DeploymentEntity` and `ResourceEntity` objects to match
  - should propagate the inherited attribute (list of `ResourceEntity` objects) with the `DeploymentEntity` objects
- some of the general matchmaking functions is generalized to the parent `Matcher` class. Many of the functions there can be overwritten to alter this default behavior.

#### `Exporter` - `from continuum_deployer.dsl.exporter.exporter import Exporter`

- `export(self, matched_resources)` - Must be implemented and takes a list of `ResourceEntity` objects that are propagated with `DeploymentEntity` objects
  - should output the results to the `output_stream` given to the `Expoter` during object initialization

### Match CLI

The `MatchCli` class is the main controller of the interactive user experience and takes care of the plumbing necessary for the [General Matchmaking Flow](#general-matchmaking-flow). It used the Python library `transitions` to build a state machine to handle the actual control flow of a CLI invocation.

## Authors

- @hassdan1 - Daniel Haß ([GitHub](https://github.com/danielhass), [GitLab](https://gitlab.com/danielhass))