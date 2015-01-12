VIRTUALENV=$(shell echo "$${VDIR:-'.env'}")
PACKAGE=ticketscloud

all: $(VIRTUALENV)

$(VIRTUALENV): requirements.txt
	[ -d $(VIRTUALENV) ] || virtualenv --no-site-packages $(VIRTUALENV)
	$(VIRTUALENV)/bin/pip install -r requirements.txt
	touch $(VIRTUALENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	@pip install bumpversion
	@bumpversion $(VERSION)
	@git checkout master
	@git merge develop
	@git checkout develop
	@git push --all
	@git push --tags

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch


.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete

.PHONY: register
# target: register - Register module on PyPi
register:
	@python setup.py register

.PHONY: upload
# target: upload - Upload module on PyPi
upload: clean
	@python setup.py sdist upload || echo 'Skip sdist upload'
	@python setup.py bdist_wheel upload || echo 'Skip bdist upload'

$(VIRTUALENV)/bin/py.test: $(VIRTUALENV) requirements-test.txt
	$(VIRTUALENV)/bin/pip install -r requirements-test.txt
	touch $(VIRTUALENV)/bin/py.test

.PHONY: test
# target: test - Runs tests
test: clean $(VIRTUALENV)/bin/py.test
	@$(VIRTUALENV)/bin/py.test -xs test_client.py

.PHONY: t
t: test

.PHONY: audit
# target: audit - Audit code
audit:
	@pip install pylama
	@pylama $(MODULE)

.PHONY: doc
doc: docs
	@pip install sphinx
	@pip install sphinx-pypi-upload
	python setup.py build_sphinx --source-dir=docs/ --build-dir=docs/_build --all-files
	python setup.py upload_sphinx --upload-dir=docs/_build/html
