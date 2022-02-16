#!/bin/bash

PYTEST_COMMAND='python -B -m pytest -vvv -rfs -p no:cacheprovider'
PYLINT_COMMAND='pylint src --fail-under=10 --output-format=json:.pylint_output.json,colorized'

run_tests() {
    $PYTEST_COMMAND $@
    if [ "$?" == "1" ]; then
        exit 1
    fi
    rm -f assets/coverage.svg
    coverage-badge > assets/coverage.svg
}

run_pylint() {
    $PYLINT_COMMAND $@
    if [ "$?" == "1" ]; then
        exit 1
    fi
}

run_mkdocs() {
    gitchangelog > docs/changelog.md
    mkdocs build
}

run_tests $@
run_pylint $@
run_mkdocs $@
