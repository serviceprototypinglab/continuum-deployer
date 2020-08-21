import pytest
from continuum_deployer.matching.matcher import Matcher
from continuum_deployer.deployment import DeploymentEntity
from continuum_deployer.resources.resource_entity import ResourceEntity


def test_upper_bound_cpu_detection():
    matcher = Matcher(
        [DeploymentEntity(name='test-deployment', memory=1024, cpu=2)],
        [ResourceEntity(name='test-node', memory=512, cpu=1)]
    )

    with pytest.raises(Exception) as e:
        matcher.match()
    assert e.type == Exception
    #assert e.value.code == 1


def test_upper_bound_memory_detection():
    matcher = Matcher(
        [DeploymentEntity(name='test-deployment', memory=2048, cpu=1)],
        [ResourceEntity(name='test-node', memory=1024, cpu=2)]
    )

    with pytest.raises(Exception) as e:
        matcher.match()
    assert e.type == Exception
    #assert e.value.code == 1
