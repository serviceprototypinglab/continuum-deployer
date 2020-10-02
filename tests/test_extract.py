import pytest
from continuum_deployer.dsl.importer.helm import Helm


@pytest.fixture(scope="function")
def extractor():
    return Helm()


def test_deployment_extract(extractor):
    stream = open('./tests/yaml/deployments.yaml', 'r')

    extractor.parse(stream)
    modules = extractor.get_app_modules()

    assert modules[0].cpu == 0.1
    assert modules[0].memory == 256
    assert modules[0].cpu_limit == 0.2
    assert modules[0].memory_limit == 512


def test_multi_component_extract(extractor):
    stream = open('./tests/yaml/multi_component.yaml', 'r')

    print(extractor.print_app_modules())

    extractor.parse(stream)
    modules = extractor.get_app_modules()

    assert len(modules) == 2


def test_replicas_extract(extractor):
    stream = open('./tests/yaml/replicas.yaml', 'r')

    extractor.parse(stream)
    modules = extractor.get_app_modules()

    assert len(modules) == 6


def test_k8s_memory_calc(extractor):
    _memory_values = [
        ['18M', 18],
        ['12Ki', 0],
        ['1.5Gi', 1610],
        ['1G', 1000],
    ]

    for memory in _memory_values:
        assert Helm.parse_k8s_memory_value(memory[0]) == memory[1]
