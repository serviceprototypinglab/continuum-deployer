import pytest
from continuum_deployer.extractors.helm import Helm


@pytest.fixture(scope="function")
def extractor():
    return Helm()


def test_resource_extract(extractor):
    stream = open('./tests/yaml/resources.yaml', 'r')

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
