# Continuum Deployer

## Setup
Install dependencies
```shell
pip install -r requirements.txt
```

## Runs tests
```shell
pytest
```

## Release
Build python package 

```shell
python setup.py bdist_wheel
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

## Authors

- @hassdan1 - Daniel Haß