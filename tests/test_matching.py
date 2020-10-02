import pytest
from continuum_deployer.solving.solver import Solver
from continuum_deployer.solving.greedy import Greedy
from continuum_deployer.resources.deployment import DeploymentEntity
from continuum_deployer.resources.resource_entity import ResourceEntity


def test_upper_bound_cpu_detection():
    matcher = Solver(
        [DeploymentEntity(name='test-deployment', memory=1024, cpu=2)],
        [ResourceEntity(name='test-node', memory=512, cpu=1)]
    )

    with pytest.raises(Exception) as e:
        matcher.match()
    assert e.type == Exception
    #assert e.value.code == 1


def test_upper_bound_memory_detection():
    matcher = Solver(
        [DeploymentEntity(name='test-deployment', memory=2048, cpu=1)],
        [ResourceEntity(name='test-node', memory=1024, cpu=2)]
    )

    with pytest.raises(Exception) as e:
        matcher.match()
    assert e.type == Exception
    #assert e.value.code == 1


def test_greedy_matcher():

    expected_results = [
        [
            DeploymentEntity(name='test-deployment-1', memory=512, cpu=2),
            DeploymentEntity(name='test-deployment-2', memory=256, cpu=0.5),
        ],
        [],
        []
    ]

    deployments = list()
    for node in expected_results:
        for deployment in node:
            deployments.append(deployment)

    matcher = Greedy(
        deployments,
        [
            ResourceEntity(name='test-node-1', memory=1024, cpu=3),
            ResourceEntity(name='test-node-2', memory=1024, cpu=3),
            ResourceEntity(name='test-node-3', memory=1024, cpu=1),
        ]
    )
    matcher.match()
    resources_matched = matcher.get_resources()

    for i, res in enumerate(resources_matched):
        for exp_deploy in expected_results[i]:
            assert exp_deploy in res.get_deployments()


def test_sat_matcher():

    expected_results = [
        [DeploymentEntity(name='test-deployment-1', memory=1024, cpu=1)],
        [
            DeploymentEntity(name='test-deployment-2', memory=512, cpu=2),
            DeploymentEntity(name='test-deployment-3', memory=256, cpu=0.5),
        ],
        []
    ]

    deployments = list()
    for node in expected_results:
        for deployment in node:
            deployments.append(deployment)

    matcher = Greedy(
        deployments,
        [
            ResourceEntity(name='test-node-1', memory=1024, cpu=1),
            ResourceEntity(name='test-node-2', memory=1024, cpu=3),
            ResourceEntity(name='test-node-3', memory=1024, cpu=1),
        ]
    )
    matcher.match()
    resources_matched = matcher.get_resources()

    for i, res in enumerate(resources_matched):
        for exp_deploy in expected_results[i]:
            assert exp_deploy in res.get_deployments()


def test_sat_matcher_with_labels():

    expected_results = [
        [DeploymentEntity(name='test-deployment-1', memory=1024, cpu=2)],
        [DeploymentEntity(name='test-deployment-2', memory=512, cpu=1), ],
        [DeploymentEntity(name='test-deployment-3', memory=256,
                          cpu=0.5, labels={'node': '3'})]
    ]

    deployments = list()
    for node in expected_results:
        for deployment in node:
            deployments.append(deployment)

    matcher = Greedy(
        deployments,
        [
            ResourceEntity(name='test-node-1', memory=1024, cpu=8),
            ResourceEntity(name='test-node-2', memory=1024, cpu=3),
            ResourceEntity(name='test-node-3', memory=1024,
                           cpu=1, labels={'node': '3'}),
        ]
    )
    matcher.match()
    resources_matched = matcher.get_resources()

    for i, res in enumerate(resources_matched):
        for exp_deploy in expected_results[i]:
            assert exp_deploy in res.get_deployments()


def test_greedy_matcher_with_labels():

    expected_results = [
        [
            DeploymentEntity(name='test-deployment-1', memory=1024, cpu=2),
            DeploymentEntity(name='test-deployment-2', memory=512, cpu=1)
        ],
        [],
        [DeploymentEntity(name='test-deployment-3', memory=256,
                          cpu=0.5, labels={'node': '3'})]
    ]

    deployments = list()
    for node in expected_results:
        for deployment in node:
            deployments.append(deployment)

    matcher = Greedy(
        deployments,
        [
            ResourceEntity(name='test-node-1', memory=4096, cpu=8),
            ResourceEntity(name='test-node-2', memory=1024, cpu=3),
            ResourceEntity(name='test-node-3', memory=1024,
                           cpu=1, labels={'node': '3'}),
        ]
    )
    matcher.match()
    resources_matched = matcher.get_resources()

    for i, res in enumerate(resources_matched):
        for exp_deploy in expected_results[i]:
            assert exp_deploy in res.get_deployments()
