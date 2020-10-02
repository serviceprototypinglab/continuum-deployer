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

## Limitations

### Helm
- Kubernetes Resources Limits are parsed and available in via the internal deployment object structure but are currently not considered by the included solvers 

## Authors

- @hassdan1 - Daniel Haß