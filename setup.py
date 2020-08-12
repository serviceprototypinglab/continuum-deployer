try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

links = []
requires = []

with open('requirements.txt') as f:
    requires = f.read().splitlines()

version = {}
with open("version.py") as fp:
    exec(fp.read(), version)

setup(
    name='splab-continuum-deployer',
    version=version.get("app_version"),
    url='https://gitlab.com/danielhass-zhaw/eva2/continuum-deployer',
    author="Daniel Haß",
    author_email="hassdan1@students.zhaw.ch",
    description='Prototypical Continuum Computing Deployer',
    long_description="Prototypical Continuum Computing Deployer",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=requires,
    dependency_links=links
)
