PKGNAME='splab-continuum-deployer'

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +

clean-build:
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info

dist:
	python setup.py bdist_wheel

install:
	pip install --user dist/*.whl

uninstall:
	pip uninstall ${PKGNAME}

install-req:
	pip3 install --user -r requirements.txt
	pip3 install --user -r requirements-dev.txt