

NAME = code-manager
VERSION = $(shell grep "__version__\s*=\s*" code_manager/version.py | sed "s/__version__\s*=\s*'\(.*\)'/\1/g")

SNAPSHOT_NAME ?= $(NAME)-$(VERSION)-$(shell git rev-parse HEAD | cut -b 1-8).tar.gz

PYTHON ?= $(shell \
	     (python -c 'import sys; sys.exit(sys.version < "2.6")' && \
	      which python) \
	     || (which python3) \
	     || (python2 -c 'import sys; sys.exit(sys.version < "2.6")' && \
	         which python2) \
	   )
ifeq ($(PYTHON),)
  $(error No suitable python found.)
endif

SETUPOPTS ?= '--record=install_log.txt'x
PYOPTIMIZE ?= 1
FILTER ?= .
PREFIX ?= /usr/local

CWD = $(shell pwd)


TEST_PATHS =  $(shell find ./code_manager -mindepth 1 -maxdepth 1 -type d \
			! -name '__pycache__' \
			! -path './code_manager/data' \
			! -path './code_manager/.mypy_cache'\
			! -path './code_manager/install_scripts')\
			./code_manager/main.py \
			./tests \
			./setup.py

help:
	@echo 'make:              Test and compile code_manager.'
	@echo 'make install:      Install $(NAME)'
	@echo 'make compile:      Byte-compile all of the python files'
	@echo 'make build:        Builds the $(NAME) and generates egg file'
	@echo 'make clean:        Remove the compiled files (*.pyc, *.pyo)'
	@echo 'make doc:          Create the pydoc documentation'
	@echo 'make test:         Test everything'
	@echo 'make snapshot:     Create a tar.gz of the current git revision'
	@echo 'make dist:         Release a new sdist to PyPI'
	@echo 'make dist_test:    Release a new sdist to PyPI (legacy)'

test: test_pylint test_flake8 test_pytest
	@echo "All test ran..."

test_pylint:
	@echo "Running pylint..."
	pylint $(TEST_PATHS)

test_flake8:
	@echo "Running flake8..."
	flake8 $(TEST_PATHS)

test_pytest:
	@echo "Running pylint..."
	pytest

snapshot:
	git archive --prefix='$(NAME)-$(VERSION)/' --format=tar HEAD | gzip > $(SNAPSHOT_NAME)

todo:
	@grep --color -Ion '\(TODO\|XXX\).*' -r ./code_manager

compile: clean
	PYTHONOPTIMIZE=$(PYOPTIMIZE) $(PYTHON) -m compileall -q ./code_manager

clean:
	@echo 'Cleaning all generated files'
	find ./code_manager -regex .\*\.py[co]\$$ -delete
	find ./code_manager -depth -name __pycache__ -type d -exec rm -r -- {} \;
	rm -rf ./build
	rm -rf ./CodeManager.egg-info
	rm -rf ./htmlcov
	rm -rf ./dist

build:
	@echo 'Building the project'
	$(PYTHON) setup.py build

install:
	@echo 'Installing on the system'
	$(PYTHON) setup.py install $(SETUPOPTS) \
		'--prefix=$(PREFIX)' '--root=$(DESTDIR)' \
		--optimize=$(PYOPTIMIZE)
coverage:
	py.test --cov=code_manager

coverage_html:
	py.test --cov=code_manager --cov-report=html $(TEST_FILES)

dist_test:
	$(PYTHON) setup.py sdist bdist_wheel;
	$(PYTHON) -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

dist:
	$(PYTHON) setup.py sdist bdist_wheel;
	$(PYTHON) -m twine upload --repository-url https://upload.pypi.org/legacy/ dist/*


.PHONY: clean compile build install
