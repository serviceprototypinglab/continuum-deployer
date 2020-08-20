import pytest
from continuum_deployer.extractors.helm import Helm

def test_resource_extract():
    stream = open('./tests/yaml/resources.yaml', 'r')

    helm = Helm()
    helm.parse(stream)
    modules = helm.get_app_modules()

    assert modules[0].resources_requests == \
        {"cpu": "100m", "memory": "256Mi"}
    assert modules[0].resources_limits == \
        {"cpu": "200m", "memory": "512Mi"}
