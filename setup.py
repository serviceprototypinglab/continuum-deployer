try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

links = []
requires = []
requires_dev = []

with open('requirements.txt') as f:
    requires = f.read().splitlines()

with open('requirements-dev.txt') as f:
    requires = f.read().splitlines()

version = {}
with open("continuum_deployer/__init__.py") as fp:
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
    extras_require={
        'dev': requires_dev
    },
    dependency_links=links,
    entry_points={
        "console_scripts": [
            "continuum-deployer = continuum_deployer.app:cli"
        ]
    }
)
