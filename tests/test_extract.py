import pytest
from continuum_deployer.helm import Helm

def test_resource_extract():
    stream = open('./tests/yaml/resources.yaml', 'r')

    helm = Helm()
    helm.parse(stream)
    deployments = helm.getDeployments()

    assert deployments[0].resources_requests == \
        {"cpu": "100m", "memory": "256Mi"}
    assert deployments[0].resources_limits == \
        {"cpu": "200m", "memory": "512Mi"}
