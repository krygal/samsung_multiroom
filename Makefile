.PHONY: build

MODULE:=samsung_multiroom

all: ensure-pip dev style checks dists test

ensure-pip:
	pip install --user --upgrade pipenv pip
	pip --version
	pipenv --version

ensure-pip-ci:
	pip install --upgrade pipenv pip
	pip --version
	pipenv --version

dev:
	pipenv install --dev
	pipenv run pip install -e .

dev-ci:
	pipenv install --dev --deploy
	pipenv run pip install -e .

style: isort autopep8 yapf

isort:
	pipenv run isort .

autopep8:
	pipenv run autopep8 --in-place --recursive setup.py $(MODULE)

yapf:
	pipenv run yapf --style .yapf --recursive -i $(MODULE)

checks: flake8 pylint

flake8:
	pipenv run python setup.py flake8

pylint:
	pipenv run pylint --rcfile=.pylintrc --output-format=colorized $(MODULE)

sc: style checks
sct: style checks test

build: dists

test:
	pipenv run pytest

test-verbose:
	pipenv run pytest -s

test-coverage:
	pipenv run py.test -v --cov $(MODULE) --cov-report term-missing --cov-report html --cov-report xml:coverage.xml

dists: requirements sdist bdist wheels

requirements:
	pipenv lock -r > requirements.txt
	pipenv lock -r -d > development.txt

release: requirements

sdist: requirements
	pipenv run python setup.py sdist

bdist: requirements
	pipenv run python setup.py bdist

wheels: requirements
	pipenv run python setup.py bdist_wheel

pypi-publish: build release
	pipenv run twine upload --repository-url=https://upload.pypi.org/legacy/ dist/*.whl

update:
	pipenv update --clear

githook: style

push: githook
	@git push origin --tags

clean:
	pipenv --rm

prepare-release: requirements

# aliases to gracefully handle typos on poor dev's terminal
check: checks
devel: dev
develop: dev
dist: dists
install: install-system
pypi: pypi-publish
styles: style
wheel: wheels
