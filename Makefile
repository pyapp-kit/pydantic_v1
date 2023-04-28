.DEFAULT_GOAL := all
sources = pydantic_v1 tests
isort = isort $(sources)
black = black -S -l 120 --target-version py38 $(sources)

.PHONY: install-linting
install-linting:
	pip install -r tests/requirements-linting.txt
	pre-commit install

.PHONY: install-pydantic
install-pydantic:
	python -m pip install -U wheel pip
	pip install -r requirements.txt
	SKIP_CYTHON=1 pip install -e .

.PHONY: install-testing
install-testing: install-pydantic
	pip install -r tests/requirements-testing.txt

.PHONY: install
install: install-testing install-linting
	@echo 'installed development requirements'

.PHONY: build-trace
build-trace:
	python setup.py build_ext --force --inplace --define CYTHON_TRACE

.PHONY: build
build:
	python setup.py build_ext --inplace

.PHONY: format
format:
	pyupgrade --py37-plus  --exit-zero-even-if-changed `find $(sources) -name "*.py" -type f`
	$(isort)
	$(black)

.PHONY: lint
lint:
	flake8 $(sources)
	$(isort) --check-only --df
	$(black) --check --diff

.PHONY: check-dist
check-dist:
	python setup.py check -ms
	SKIP_CYTHON=1 python setup.py sdist
	twine check dist/*

.PHONY: mypy
mypy:
	mypy pydantic_v1

.PHONY: pyupgrade
pyupgrade:
	pyupgrade --py37-plus `find pydantic_v1 tests -name "*.py" -type f`

.PHONY: pyright
pyright:
	cd tests/pyright && pyright

.PHONY: test
test:
	pytest --cov=pydantic_v1

.PHONY: testcov
testcov: test
	@echo "building coverage html"
	@coverage html

.PHONY: testcov-compile
testcov-compile: build-trace test
	@echo "building coverage html"
	@coverage html

.PHONY: all
all: lint mypy testcov

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]'`
	rm -f `find . -type f -name '*~'`
	rm -f `find . -type f -name '.*~'`
	rm -rf .cache
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	rm -f pydantic_v1/*.c pydantic_v1/*.so
	python setup.py clean
	rm -rf site
	rm -rf fastapi/test.db
	rm -rf coverage.xml
